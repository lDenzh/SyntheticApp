import React, {useRef, useState} from "react";
import {uploadSuccess, setUploadSuccess} from "./App";
import axios, {isAxiosError} from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button } from 'reactstrap';
import "./Functions.css";

import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import PDFevaluate from "./PDFevaluate";



const Functions = (props) => {
    const [file, setFile] = useState<any | null>();
    const inputRef = useRef();

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
    };

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setFile(e.dataTransfer.files)
    };
  
    const toBase64 = file => new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file[0]);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });

    async function Postman() {
        let myPDF = await toBase64(file)
        let myArray = myPDF.split(",")
        let word = myArray[1];

        const payload = {
            PDF: word,
            GT: updated 
        };
        console.log(payload);

        const { data } = await axios.post("http://localhost:8000/runSynth", payload, {  //
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json'
              },
              
        })
        
        console.log(data);
       
    }

    const handleUpload = () => {
        Postman();
        props.onDisplayChange(true);
    }

    const gtRef = useRef(null);
    const [gt, setGt] = useState('')
    const [updated, setUpdated] = useState(gt)
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setGt(e.target.value)
    }

    const handleGT = () => {
        setUpdated(gt)
        console.log(updated)
        
    }

    //PDF renderer
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
  
    function onDocumentLoadSuccess({ numPages }) {
      setNumPages(numPages);
      setPageNumber(1);
    }
  
    function changePage(offset) {
      setPageNumber(prevPageNumber => prevPageNumber + offset);
    }
  
    function previousPage() {
      changePage(-1);
    }
  
    function nextPage() {
      changePage(1);
    }

    

    if (file) return (
      
    <div style={{display: "flex", flexDirection: "row"}}>
      <div className="uploads">
            <ul>
                {Array.from(file).map((file, idx) => <li key={idx}>{file.name}</li> )}
            </ul>
            <div className ="input-container">
                <textarea 
                    id="inputfield"
                    ref={gtRef}
                    type="text"
                    onChange={handleChange}
                    placeholder='    
{
    "label": "Navn",
    "value": "Navn Navnesen"
},
{
    "label": "Totalsum",
    "value": "528.00 kr"
},
{
    "label": "Telefon",
    "value": "+4794721323"
}
                '
                    
                />
            </div>
                <Button color="danger" onClick={() => setFile(null)}>Cancel</Button>
                <Button color="secondary" onClick={handleGT}>Confirm GT</Button>
                <Button color="primary" id="hidden" onClick={handleUpload}>Upload to server</Button>
        </div>
      <div style={{marginLeft: "60px"}}>
        <Document
            file={file[0]}
            onLoadSuccess={onDocumentLoadSuccess}>
          <Page pageNumber={pageNumber} renderTextLayer={false}/>
        </Document>
              <div>
      <p>
        Page {pageNumber || (numPages ? 1 : '--')} of {numPages || '--'}
      </p>
      <div className="btnprevnext">
        <Button
          type="Button"
          disabled={pageNumber <= 1}
          onClick={previousPage}
        >
          Previous
        </Button>
        <Button
          type="Button"
          disabled={pageNumber >= numPages}
          onClick={nextPage}
        >
          Next
        </Button>
      </div>
    </div>
      </div>
    </div>
      
  )
    return (
        <>
            {!file && (
            <div
                className="dropzone"
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <h1>Drag and drop or select from file explorer to upload</h1>
                <input
                    type = 'file'
                    accept= 'application/pdf'
                    onChange={(event) => setFile(event.target.files)}
                    hidden
                    ref = {inputRef}
                />
                <Button color="primary" onClick = {() => inputRef.current.click()}>Choose file</Button>
            </div>
            )}
        </>
    )
}

export default Functions;