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

app = Sanic(__name__)   

CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

## #may use later
#cursor.execute("SELECT version();")
#result = cursor.fetchone()
#print(f'Connected to {result} \n')


# @app.route('/test', methods=['GET'])
# async def hello(request):
#     return text("Backend runs on localhost:8000")

# @app.route('/data', methods=['GET'])
# async def data(request):
#     return sanic_json({"message": "Hello from the backend-boi!"})


# @app.route('/posty', methods=['POST'])
# @cors(allow_methods="POST")
# async def post_json(request):

#     return sanic_json({ "received": True, "message": request.json })



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
    row_pointer = 0
        
    # check if the request contains a json
    if not request.json:
        return sanic_json({ "received": False, "message": "No JSON received in request"})
    

    # import pdb; pdb.set_trace()
    with tempfile.TemporaryDirectory(prefix='TemporaryDirectory_') as destdir:
        print(destdir)
        json_data = json.loads(request.json)
        ##import pdb; pdb.set_trace()
        pdf_path = Path(f'{destdir}/dataPDF.pdf') # Creates a path and creates a pdf file
        gt_path = Path(f'{destdir}/dataGT.json') # Creates a path and creates a json file

        pdf_path.write_bytes(b64decode(json_data["PDF"].encode('utf-8'))) #writes the pdf to the path
        gt_path.write_text(json.dumps(json_data["GT"])) #writes the json to the path
    
        dest_dir = Path(destdir)
        temp_dir = Path(f'{destdir}/tmpdirFlattened')
        
        status = synthesize_document(pdf_path,gt_path,dest_dir,temp_dir)
        
        pdf_collection = list(dest_dir.glob('**/*.pdf'))
        gt_collection = list(dest_dir.glob('**/*.json'))
        
        # json_statment = {
        #     "PDF" : {},
        #     "GT" : {}
        # }

        #adds the pdfs and gts to the json
        if len(pdf_collection) != len(gt_collection):
            return sanic_json({ "received": False, "status": status, "message": "Number of PDFs and GTs are not equal"})
        
        for i in range(len(pdf_collection)): 
            #add pdf to synthesized table
            cursor.execute("INSERT INTO synthesized (pdf, gt) VALUES (%s, %s)", (b64encode(pdf_collection[i].read_bytes()).decode('utf-8'), gt_collection[i].read_text()))
            conn.commit()

        print("SOMETHING WITTY HERE")
            #encoded_pdf = b64encode(pdf.read_bytes())
            #raw_pdf = encoded_pdf.decode('utf-8')
            
        

            #json_statment["PDF"][pdf.name] = raw_pdf
        # del json_statment["PDF"]["dataPDF.pdf"]

        # for gt in gt_collection:
        #     json_statment["GT"][gt.name] = gt.read_text()
        # del json_statment["GT"]["dataGT.json"]

        # return_statement = json.dumps(json_statment
        # Get first row of the table

        cursor.execute("SELECT * FROM synthesized WHERE id = %s;", [2])
        row_pointer+=1
        row = cursor.fetchone()
        json_statment = {
            "PDF" : bytes(row[1]).decode('utf-8'),
            "GT" : json.loads(row[2])
        }

        return_statement = json.dumps(json_statment)


        return sanic_json({ "received": True, "status": status, "message": return_statement})

# GET request to get the certaion row from the database using the row_pointer-variable
@app.route('/getSynth', methods=['GET'])
@cors(allow_methods="GET")
def getSynth(request):

    cursor.execute("SELECT * FROM synthesized WHERE id = %s;", (row_pointer,))
    row = cursor.fetchone()
    row_pointer += 1
    #return sanic_json({ "received": True, "pdf": b64encode(row[1]).decode('utf-8'), "gt": row[2]})
    return sanic_json({ "received": True, "pdf": bytes(row[1]).decode('utf-8'), "gt": json.loads(row[2])})


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

                


    except (Exception, psycopg2.Error) as error:
        print("Unable to connect to database", error)
# finally:
#     if (conn):
#         cursor.close()
#         conn.close()
#         print("Connection closed \n")
