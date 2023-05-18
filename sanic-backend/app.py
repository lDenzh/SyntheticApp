import json
import logging
import os
from base64 import b64decode, b64encode
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg2
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
    org_id = 1
    # check if the request contains a json
    if not request.json:
        return sanic_json({"received": False,
                           "message": "No JSON received in request"})

    global conn
    global cursor
    if conn is None:
        
        conn = psycopg2.connect(
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            port="5432",
            host="database"
        )
        cursor = conn.cursor()
        conn.autocommit = True
        cursor.execute("DROP TABLE IF EXISTS synthesized;")

    # Connect to the database
    
    cursor.execute(
        """CREATE TABLE synthesized
        (id SERIAL PRIMARY KEY, pdf bytea, 
         gt VARCHAR, orgID INTEGER);""")

    with TemporaryDirectory() as destdir:
        json_data = request.json

        pdf_path = Path(f'{destdir}/dataPDF.pdf')
        gt_path = Path(f'{destdir}/dataGT.json')

        pdf_path.write_bytes(b64decode(json_data["PDF"]))
        gt_path.write_text(json_data["GT"])

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
            #data = b64encode(pdf_collection[i].read_bytes()).decode('utf-8')
            cursor.execute("INSERT INTO synthesized (pdf, gt, orgID) VALUES (%s, %s, %s)",
                           (pdf_collection[i].read_bytes(), gt_collection[i].read_text(), org_id))

        return text("Synthesized")


# GET request to get the certain row from the database
@app.route('/documents/<documentId>', methods=['GET'])
@cors(allow_methods="GET")
def fetch_document(request, documentId):

    logging.info("Fetching document")
    cursor.execute("SELECT * FROM synthesized WHERE id = %s;", (documentId,))
    row = cursor.fetchone()
    json_statement = create_statement(row[1], row[2], row[3])
    
    return sanic_json({"received": True, "message": json_statement})


# DELETE request that deletes the row with the given id
@app.route('/documents/<documentId>', methods=['DELETE'])
@cors(allow_methods="DELETE")
def delete_document(request, documentId):
    cursor.execute("DELETE FROM synthesized WHERE id = %s;", (documentId,))
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
                                                       data_pair[2],
                                                       data_pair[3])

    return sanic_json({"received": True, "message": json_statment})

# # GET request that returns the all the rows accoring to the orgID
# @app.route('/documents/<orgId>', methods=['GET'])
# @cors(allow_methods="GET")
# def all_documents_org(request, orgId):
#     cursor.execute("SELECT * FROM synthesized WHERE orgID = %s;", (orgId,))
#     data = cursor.fetchall()
#     json_statment = {}
#     for data_pair in data:
#         json_statment[data_pair[0]] = create_statement(data_pair[1],
#                                                        data_pair[2],
#                                                        data_pair[3])

#     return sanic_json({"received": True, "message": json_statment})

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


def create_statement(pdf_value, gt_value, org_id):
    return {
        "PDF": b64encode(bytes(pdf_value)).decode('utf-8'),
        "GT": json.loads(gt_value),
        "orgID": org_id
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
