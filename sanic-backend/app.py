import json
import logging
import os
import webbrowser
from base64 import b64decode, b64encode
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg2
from sanic import Sanic
from sanic.response import json as sanic_json, text as sanic_text
from sanic_cors.extension import CORS
from sanic_ext import Extend, cors
from synthetic.pdf.parser import parse_pdf
from synthetic.pdf.synthesizer import BasicSynthesizer


app = Sanic(__name__)   # Create a Sanic app

conn = None
cursor = None
#webbrowser.open("localhost:5173", new=2, autoraise=True)
CORS_OPTIONS = {
    "resources": r'/*',
    "origins": "*",
    "methods": ["GET", "POST", "HEAD", "OPTIONS", "DELETE"]
    }
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS],
       config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})


# POST request that synthesizes the pdf and gt
@app.route('/synthesizer/<orgId>', methods=['POST'])
@cors(allow_methods="POST")
def run_synthsizer(request, orgId):

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

        pdf_collection = sorted(
            list(dest_dir.glob('**/*.pdf')), key=lambda x: x.name
            )

        gt_collection = sorted(
            list(dest_dir.glob('**/*.json')), key=lambda x: x.name
            )

        if pdf_collection[-1].name != "dataPDF.pdf":
            return sanic_json({"received": False,
                               "message": "PDF not handled correctly"})
        if gt_collection[-1].name != "dataGT.json":
            return sanic_json({"received": False,
                               "message": "GT not handled correctly"})

        del pdf_collection[-1]
        del gt_collection[-1]

        for i in range(len(pdf_collection)):
            # add pdf to synthesized table
            cursor.execute("""INSERT INTO synthesized (pdf, gt, orgID)
                           VALUES (%s, %s, %s)""",
                           (pdf_collection[i].read_bytes(),
                            gt_collection[i].read_text(), orgId))

        return sanic_text(status)


# GET request to get the certain row from the database
@app.route('/documents/<orgId>/<documentId>', methods=['GET'])
@cors(allow_methods="GET")
def fetch_document(request, orgId, documentId):

    logging.info("Fetching document")
    cursor.execute("""SELECT * FROM synthesized
                   WHERE id = %s AND orgId = %s""", (documentId, orgId))
    row = cursor.fetchone()
    json_statement = create_statement(row[1], row[2], row[3])

    return sanic_json({"received": True, "message": json_statement})


# DELETE request that deletes the row with the given id
@app.route('/documents/<orgId>/<documentId>', methods=['DELETE'])
@cors(allow_methods="DELETE")
def delete_document(request, orgId, documentId):
    cursor.execute("DELETE FROM synthesized WHERE id = %s AND orgId = %s;",
                   (documentId, orgId))
    return sanic_text("Deleted")


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


# GET request that returns the all the rows accoring to the orgID
@app.route('/documents/<orgId>', methods=['GET'])
@cors(allow_methods="GET")
def all_documents_org(request, orgId):
    cursor.execute("SELECT * FROM synthesized WHERE orgID = %s;", (orgId,))
    data = cursor.fetchall()
    json_statment = {}
    for data_pair in data:
        json_statment[data_pair[0]] = create_statement(data_pair[1],
                                                       data_pair[2],
                                                       data_pair[3])

    return sanic_json({"received": True, "message": json_statment})


# Synthesizes the pdf and gt
def synthesize_document(
        pdf_path: Path, ground_truth: Path,
        dest_dir: Path, temp_dir: Path):
    status = parse_pdf(
        name='pdf_to_synthesize',
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


def sort_name(file_name):
    return len(file_name.name)


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
