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



app = Sanic(__name__)   

CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

@app.route('/test', methods=['GET'])
async def hello(request):
    return text("Backend runs on localhost:8000")

@app.route('/data', methods=['GET'])
async def data(request):
    return sanic_json({"message": "Hello from the backend-boi!"})


@app.route('/posty', methods=['POST'])
@cors(allow_methods="POST")
async def post_json(request):

    return sanic_json({ "received": True, "message": request.json })
 


@app.route('/runSynth', methods=['POST'])
@cors(allow_methods="POST")
def post_runSynth(request):
    # import pdb; pdb.set_trace()
    with tempfile.TemporaryDirectory(prefix='TemporaryDirectory_') as destdir:
        print(destdir)
        json_data = json.loads(request.json)
        ##import pdb; pdb.set_trace()
        pdf_path = Path(f'{destdir}/dataPDF.pdf')
        gt_path = Path(f'{destdir}/dataGT.json')

        pdf_path.write_bytes(b64decode(json_data["PDF"].encode('utf-8')))
        gt_path.write_text(json.dumps(json_data["GT"]))
     
        dest_dir = Path(destdir)
        temp_dir = Path(f'{destdir}/tmpdirFlattened')
        
        status = synthesize_document(pdf_path,gt_path,dest_dir,temp_dir)
        
        pdf_collection = list(dest_dir.glob('**/*.pdf'))
        gt_collection = list(dest_dir.glob('**/*.json'))
        
        json_statment = {
            "PDF" : {},
            "GT" : {}
        }

        #adds the pdfs and gts to the json
        for pdf in pdf_collection:
            encoded_pdf = b64encode(pdf.read_bytes())
            raw_pdf = encoded_pdf.decode('utf-8')
            json_statment["PDF"][pdf.name] = raw_pdf
        del json_statment["PDF"]["dataPDF.pdf"]

        for gt in gt_collection:
            json_statment["GT"][gt.name] = gt.read_text()
        del json_statment["GT"]["dataGT.json"]

        return_statement = json.dumps(json_statment)

        return sanic_json({ "received": True, "status": status, "message": return_statement})
    

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
    app.run(host="0.0.0.0", port=8000, debug=True)

