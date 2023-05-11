from sanic import Sanic
from sanic.response import json as sanic_json, text 
from sanic import text
from sanic_ext import Extend, cors
from sanic_cors.extension import CORS


import json
import tempfile
from pathlib import Path
from base64 import b64decode, b64encode
from synthetic.pdf.parser import parse_pdf
from synthetic.pdf.synthesizer import BasicSynthesizer
import psycopg2

app = Sanic(__name__)   # Create a Sanic app


CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

@app.route('/runSynth', methods=['POST'])
@cors(allow_methods="POST")
def post_runSynth(request):

    # Connect to the database   
    global conn
    conn = psycopg2.connect(
        database="storage_db",
        user="postgres_usr",
        password="postgres_pwd",
        port="5432",
        host="database"
    )
    global cursor
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS synthesized (id SERIAL PRIMARY KEY, pdf bytea, gt varchar);")
    conn.commit()
    row_pointer = 1
        
    # check if the request contains a json
    if not request.json:
        return sanic_json({ "received": False, "message": "No JSON received in request"})
    else:
        with tempfile.TemporaryDirectory(prefix='TemporaryDirectory_') as destdir:
            print(destdir)
            json_data = request.json

            pdf_path = Path(f'{destdir}/dataPDF.pdf') # Creates a path and creates a pdf file
            gt_path = Path(f'{destdir}/dataGT.json') # Creates a path and creates a json file

            pdf_path.write_bytes(b64decode(json_data["PDF"].encode('utf-8'))) #writes the pdf to the path
            gt_path.write_text(json.dumps(json_data["GT"])) #writes the json to the path
        
            dest_dir = Path(destdir)
            temp_dir = Path(f'{destdir}/tmpdirFlattened')
            
            status = synthesize_document(pdf_path,gt_path,dest_dir,temp_dir)
            
            pdf_collection = list(dest_dir.glob('**/*.pdf'))
            gt_collection = list(dest_dir.glob('**/*.json'))
            

            #adds the pdfs and gts to the json
            if len(pdf_collection) != len(gt_collection):
                return sanic_json({ "received": False, "status": status, "message": "Number of PDFs and GTs are not equal"})
            
            for i in range(len(pdf_collection)): 
                #add pdf to synthesized table
                cursor.execute("INSERT INTO synthesized (pdf, gt) VALUES (%s, %s)", (b64encode(pdf_collection[i].read_bytes()).decode('utf-8'), gt_collection[i].read_text()))
                conn.commit()
                            
                #json_statment["PDF"][pdf.name] = raw_pdf
            # del json_statment["PDF"]["dataPDF.pdf"]

            # for gt in gt_collection:
            #     json_statment["GT"][gt.name] = gt.read_text()
            # del json_statment["GT"]["dataGT.json"]

            # return_statement = json.dumps(json_statment
            # Get first row of the table

            cursor.execute("SELECT * FROM synthesized WHERE id = %s;", [row_pointer])
            row_pointer+=1
            row = cursor.fetchone()
            json_statment = {
                "PDF" : b64encode(bytes(row[1])).decode('utf-8'),
                "GT" : json.loads(row[2])
            }

            return sanic_json({ "received": True, "status": status, "message": json.dumps(json_statment)})

# GET request to get the certain row from the database using the row_pointer-variable
@app.route('/getDATA', methods=['GET'])
@cors(allow_methods="GET")
def getSynth(request):

    cursor.execute("SELECT * FROM synthesized WHERE id = %s;", (row_pointer,))
    row = cursor.fetchone()
    row_pointer += 1
    json_statment = {
        "PDF" : b64encode(bytes(row[1])).decode('utf-8'),
        "GT" : json.loads(row[2])
    }
    return sanic_json({ "received": True, "message": json.dumps(json_statment)})


# POST request that checks if the json is eligible
@app.route('/testJSON', methods=['POST'])
@cors(allow_methods="POST")
def testJSON(request):
    try:
        json.loads(request.json)
        return text("Eligible JSON")
    except:
        return text("Not eligible JSON")

# DELETE request that deletes the row with the given id
@app.route('/deleteSynth', methods=['DELETE'])
@cors(allow_methods="DELETE")
def deleteSynth(request):
    cursor.execute("DELETE FROM synthesized WHERE id = %s;", request.json["id"])
    conn.commit()
    return text("Deleted")

# GET request that returns the all the rows in the database
@app.route('/getAllDATA', methods=['GET'])
@cors(allow_methods="GET")
def getAllDATA(request):
    cursor.execute("SELECT * FROM synthesized;")
    rows = cursor.fetchall()
    json_statment = {}
    for row in rows:
        json_statment[row[0]] = {
            "PDF" : b64encode(bytes(row[1])).decode('utf-8'),
            "GT" : json.loads(row[2])
        }
    return sanic_json({ "received": True, "message": json.dumps(json_statment)})




# Synthesizes the pdf and gt
def synthesize_document(pdf_path:Path, ground_truth:Path, dest_dir:Path, temp_dir:Path):

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


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8000, debug=True)
    except psycopg2.Error as DB_error :
        print("Unable to connect to database", DB_error)
    except Exception as App_error:
            print("Server shut down", App_error)
    finally:
        if (conn):
            cursor.close()
            conn.close()
            print("Connection closed \n")
