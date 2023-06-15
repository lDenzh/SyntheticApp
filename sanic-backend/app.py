import json
import logging
import os
import webbrowser
from base64 import b64decode, b64encode
from pathlib import Path
from tempfile import TemporaryDirectory

import psycopg2
import psycopg2.extras
from sanic import Sanic
from sanic.response import json as sanic_json, text as sanic_text
from sanic_cors.extension import CORS
from sanic_ext import Extend, cors
from synthetic.pdf.parser import parse_pdf
from synthetic.pdf.synthesizer import BasicSynthesizer


app = Sanic(__name__)   # Create a Sanic app
conn = None
cursor = None
webbrowser.open('localhost:5173', new=2, autoraise=True)

CORS_OPTIONS = {
    'resources': r'/*',
    'origins': '*',
    'methods': ['GET', 'POST', 'HEAD', 'OPTIONS', 'DELETE']
    }
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS],
       config={'CORS': False, 'CORS_OPTIONS': CORS_OPTIONS})


# POST request that synthesizes the pdf and gt
@app.route('/synthesizer/<documentId>', methods=['POST'])
@cors(allow_methods='POST')
def run_synthsizer(request, documentId):

    # check if the request contains a json
    if not request.json:
        return sanic_json({'received': False,
                           'message': 'No JSON received in request'})

    global conn
    global cursor
    if not conn:

        conn = psycopg2.connect(
            database=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            port='5432',
            host='database'
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = True
        cursor.execute('DROP TABLE IF EXISTS synthesized;')

        # Connect to the database
        cursor.execute(
            '''CREATE TABLE synthesized
            (id SERIAL PRIMARY KEY, pdf bytea,
            gt VARCHAR, documentId INTEGER);''')

    with TemporaryDirectory() as destdir:
        json_data = request.json

        pdf_path = Path(f'{destdir}/dataPDF.pdf')
        gt_path = Path(f'{destdir}/dataGT.json')

        pdf_path.write_bytes(b64decode(json_data['PDF']))
        gt_path.write_text(json_data['GT'])

        dest_dir = Path(destdir)
        temp_dir = Path(f'{destdir}/tmpdirFlattened')

        status = synthesize_document(pdf_path, gt_path, dest_dir, temp_dir)

        pdf_collection = sorted(
            list(dest_dir.glob('**/*.pdf')), key=lambda x: x.name
            )

        gt_collection = sorted(
            list(dest_dir.glob('**/*.json')), key=lambda x: x.name
            )

        result = zip(pdf_collection, gt_collection)

        for pdf_path, gt_path in result:
            # add pdf to synthesized table
            if pdf_path.name == 'dataPDF.pdf':
                continue
            cursor.execute('''INSERT INTO synthesized (pdf, gt, documentId)
                           VALUES (%s, %s, %s)''',
                           (pdf_path.read_bytes(),
                            gt_path.read_text(),
                            documentId
                            ))

        return sanic_text(status)


# GET request to get the certain row from the database
# @app.route('/documents/<syntheticId>', methods=['GET'])
# @cors(allow_methods='GET')
# def fetch_document(request, documentId, syntheticId):

    logging.info('Fetching document')
    cursor.execute('''SELECT * FROM synthesized
                   WHERE id = %s AND documentId = %s''',
                   (syntheticId,
                    documentId))
    ret_dict = cursor.fetchone()
    json_statement = create_statement(
                                     ret_dict['pdf'],
                                     ret_dict['gt'],
                                     ret_dict['documentid']
                                     )

    return sanic_json({'received': True, 'message': json_statement}) 


# DELETE request that deletes the row with the given id
@app.route('/documents/<syntheticId>', methods=['DELETE'])
@cors(allow_methods='DELETE')
def delete_document(request, documentId, syntheticId):
    cursor.execute(
        'DELETE FROM synthesized WHERE id = %s AND documentId = %s;',
        (syntheticId, documentId),
    )
    return sanic_text('Deleted')


# GET request that returns the all the rows in the database
@app.route('/documents', methods=['GET'])
@cors(allow_methods='GET')
def all_documents(request):
    cursor.execute('SELECT * FROM synthesized;')
    data_table = cursor.fetchall()
    json_statment = {}
    for data_row in data_table:
        json_statment[data_row['id']] = create_statement(
            data_row['pdf'],
            data_row['gt'],
            data_row['documentId']
            )

    return sanic_json({'received': True, 'message': json_statment})


# GET request that returns the all the rows accoring to the documentId
@app.route('/documents/<documentId>', methods=['GET'])
@cors(allow_methods='GET')
def all_documents_by_Id(request, documentId):
    cursor.execute('SELECT * FROM synthesized WHERE documentId = %s;',
                   (documentId,))
    data_table = cursor.fetchall()
    json_statment = {}
    for data_row in data_table:
        json_statment[data_row['id']] = create_statement(
            data_row['pdf'],
            data_row['gt'],
            data_row['documentId'],
        )

    return sanic_json({'received': True, 'message': json_statment})


# Synthesizes the pdf and gt
def synthesize_document(
        pdf_path: Path,
        ground_truth: Path,
        dest_dir: Path,
        temp_dir: Path,
        pdf_name='pdf_to_synthesize',
        synthesizer_class=BasicSynthesizer,
        num_outputs_per_document=10,
        max_fonts=10,
        max_pages=3
        ):

    status = parse_pdf(
        name=pdf_name,
        pdf_file=pdf_path,
        json_file=ground_truth,
        synthesizer_class=synthesizer_class,
        num_outputs_per_document=num_outputs_per_document,
        dst_dir=dest_dir,
        tmp_dir=temp_dir,
        max_fonts=max_fonts,
        max_pages=max_pages
    )
    return status


def create_statement(pdf_value, gt_value, document_id):
    return {
        'pdf': b64encode(bytes(pdf_value)).decode('utf-8'),
        'gt': json.loads(gt_value),
        'documentId': document_id
    }


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8000, debug=True)
    except psycopg2.Error as DB_error:
        print('Unable to connect to database', DB_error)
    except Exception as App_error:
        print('Server shut down', App_error)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print('Connection closed \n')
