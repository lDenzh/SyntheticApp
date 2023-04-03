from sanic import Sanic
from sanic.response import json as sanicJSON, text 
from sanic import text #vet ikke om trenger?
from sanic_ext import Extend, cors
from sanic_cors.extension import CORS

import logging
import tempfile
from pathlib import Path
from base64 import b64decode, b64encode
from synthetic.pdf.parser import parse_pdf
from synthetic.pdf.synthesizer import BasicSynthesizer
import os


app = Sanic(__name__)   

CORS_OPTIONS = {"resources": r'/*', "origins": "*", "methods": ["GET", "POST", "HEAD", "OPTIONS"]}
# Disable sanic-ext built-in CORS, and add the Sanic-CORS plugin
Extend(app, extensions=[CORS], config={"CORS": False, "CORS_OPTIONS": CORS_OPTIONS})

@app.route('/test', methods=['GET'])
async def hello(request):
    return text("Backend runs on localhost:8000")

@app.route('/data', methods=['GET'])
async def data(request):
    return sanicJSON({"message": "Hello from the backend-boi!"})


@app.route('/posty', methods=['POST'])
@cors(allow_methods="POST")
async def post_json(request):

    return sanicJSON({ "received": True, "message": request.json })
 


@app.route('/runSynth', methods=['POST'])
@cors(allow_methods="POST")
async def post_runSynth(request):

    with tempfile.TemporaryDirectory(prefix='TemporaryDirectory_') as tmpdir:
        path_flattened = f'{tmpdir}/tmpdirFlattened'
        os.mkdir(path_flattened)
        json_data = request.json
        pdf_path = Path(f'{tmpdir}/dataPDF.pdf')
        GT_path = Path(f'{tmpdir}/dataGT.json')
        pdf_path.write_bytes(b64decode(json_data["PDF"]))
        pdf_path.write_text(json_data["GT"])
            
        status = synthesize_document(pdf_path,GT_path,tmpdir,path_flattened)

        return sanicJSON({ "received": True, "message": "its all gooood in da hood"})
    
    

def synthesize_document(pdf_path:Path, ground_truth:Path, dest_dir:Path, temp_dir:Path):

    status = parse_pdf(
        name='parseX',
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

