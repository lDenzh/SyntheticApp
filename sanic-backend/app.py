from base64 import b64decode, b64encode
import json
import logging
from pathlib import Path
import psycopg2
from tempfile import TemporaryDirectory

from sanic import Sanic
from sanic.response import json as sanic_json, text

from sanic_cors.extension import CORS
from sanic_ext import Extend, cors

from synthetic.pdf.parser import parse_pdf
from synthetic.pdf.synthesizer import BasicSynthesizer


app = Sanic(__name__)   # Create a Sanic app
conn = None
cursor = None

CORS_OPTIONS = {
    "resources": r'/*',
    "origins": "*",
    "methods": ["GET", "POST", "HEAD", "OPTIONS"]
    }
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS],
       config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})


# POST request that synthesizes the pdf and gt
@app.route('/synthesizer', methods=['POST'])
@cors(allow_methods="POST")
def run_synthsizer(request):

    # check if the request contains a json
    if not request.json:
        return sanic_json({"received": False,
                           "message": "No JSON received in request"})

    global conn
    global cursor
    conn = psycopg2.connect(
        database="storage_db",
        user="postgres_usr",
        password="postgres_pwd",
        port="5432",
        host="database"
    )

    cursor = conn.cursor()

    # Connect to the database
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS synthesized
        (id SERIAL UNIQUE PRIMARY KEY, pdf bytea, gt varchar);""")
    conn.commit()

    with TemporaryDirectory() as destdir:
        json_data = request.json

        pdf_path = Path(f'{destdir}/dataPDF.pdf')
        gt_path = Path(f'{destdir}/dataGT.json')

        pdf_path.write_bytes(b64decode(json_data["PDF"].encode('utf-8')))
        gt_path.write_text(json.dumps(json_data["GT"]))

        dest_dir = Path(destdir)
        temp_dir = Path(f'{destdir}/tmpdirFlattened')

        status = synthesize_document(pdf_path, gt_path, dest_dir, temp_dir)

        pdf_collection = list(dest_dir.glob('**/*.pdf'))
        gt_collection = list(dest_dir.glob('**/*.json'))

        # adds the pdfs and gts to the json
        if len(pdf_collection) != len(gt_collection):
            return sanic_json({"received": False, "status": status,
                               "message":
                               "Number of PDFs and GTs are not equal"})

        for i in range(len(pdf_collection)):
            # add pdf to synthesized table
            cursor.execute("INSERT INTO synthesized (pdf, gt) VALUES (%s, %s)",
                           (b64encode(pdf_collection[i].read_bytes()).decode('utf-8'),
                            gt_collection[i].read_text()))
            conn.commit()

        cursor.execute("SELECT * FROM synthesized WHere id = 1;")
        data_from_db = cursor.fetchone()
        logging.info(data_from_db)

        return text("Synthesized")


# GET request to get the certain row from the database
@app.route('/documents/<document_id>', methods=['GET'])
@cors(allow_methods="GET")
def fetch_document(request, document_id):
    get_id = request.path.split("/")[-1]
    print(get_id)
    logging.info("Fetching document")

    cursor.execute("SELECT * FROM synthesized WHERE id = %s;", (document_id,))
    row = cursor.fetchone()
    json_statement = create_statement(row[1], row[2])
    print(json_statement["GT"])
    return sanic_json({"received": True,
                       "message": json.dumps(json_statement)})


# POST request that checks if the json is eligible
# @app.route('/testJSON', methods=['POST'])
# @cors(allow_methods="POST")
# def testJSON(request):
#     try:
#         json.loads(request.json)
#         return text("Eligible JSON")
#     except:
#         return text("Not eligible JSON")

# DELETE request that deletes the row with the given id
@app.route('/documents/<id>', methods=['DELETE'])
@cors(allow_methods="DELETE")
def delete_document(request, document_id):
    get_id = request.path.split("/")[-1]
    cursor.execute("DELETE FROM synthesized WHERE id = %s;", (get_id,))
    conn.commit()
    return text("Deleted")


# GET request that returns the all the rows in the database
@app.route('/documents', methods=['GET'])
@cors(allow_methods="GET")
def all_documents(request):
    cursor.execute("SELECT * FROM synthesized;")
    data = cursor.fetchall()
    json_statment = {}
    for data_pair in data:
        json_statment[data_pair[0]] = create_statement(data_pair[1],
                                                       data_pair[2])

    return sanic_json({"received": True, "message": json.dumps(json_statment)})


# Synthesizes the pdf and gt
def synthesize_document(
        pdf_path: Path, ground_truth: Path,
        dest_dir: Path, temp_dir: Path):

    status = parse_pdf(
        name='pdf_test',
        pdf_file=pdf_path,
        json_file=ground_truth,
        synthesizer_class=BasicSynthesizer,
        num_outputs_per_document=10,
        dst_dir=dest_dir,
        tmp_dir=temp_dir,
        max_fonts=10,
        max_pages=3
    )
    return status


def create_statement(pdf_value, gt_value):
    return {
        "PDF": b64encode(bytes(pdf_value)).decode('utf-8'),
        "GT": json.loads(gt_value)
    }


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8000, debug=True)
    except psycopg2.Error as DB_error:
        print("Unable to connect to database", DB_error)
    except Exception as App_error:
        print("Server shut down", App_error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Connection closed \n")
