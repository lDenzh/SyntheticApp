import React, {useEffect, useRef, useState} from "react";
import axios, {isAxiosError} from "axios";
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button } from 'reactstrap';
import "./Functions.css";

import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";




const Functions = (props: any) => {
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
        
        props.onChange(); //Increment docID counter in <App/>
        let docID = props.onload(); //Get docID from <App/>
        console.log("this.docID = "+docID);

        const { data } = await axios.post("http://localhost:8000/synthesizer/"+docID, payload, {  
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json'
              },
              
        })
      ;
       
       console.log(JSON.stringify(data));
       props.onDisplayChange(true);
    }

    const handleUpload = async() => {
        Postman();
    }

    const gtRef = useRef(null);
    const [gt, setGt] = useState('')
    const [updated, setUpdated] = useState(gt)
    
    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setGt(e.target.value)
    }

    const handleGT = () => {
        setUpdated(gt)
        console.log(updated) //Shows the GT in console
    }

    //PDF renderer
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
  
    function onDocumentLoadSuccess({ numPages }) {
      setNumPages(numPages);
      setPageNumber(1);
    }
  
    function changePage(offset:number) {
      setPageNumber(prevPageNumber => prevPageNumber + offset);
    }
  
    function previousPage() {
      changePage(-1);
    }
  
    function nextPage() {
      changePage(1);
    }

    

    if (file) return (
      
    <div style={{display: "flex", flexDirection: "row", justifyContent: "center"}}>
      <div className="uploads">
            <ul>
                {Array.from(file).map((file, idx) => <li key={idx}>{file.name}</li> )}
            </ul>
            
            <div className ="input-container">
                <textarea 
                    id="inputfield"
                    ref={gtRef}
                    onChange={handleChange}
                    placeholder='    
[{
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
}]
                '
                    
                />
            </div>
                <Button color="danger" onClick={() => setFile(null)}>Cancel</Button>
                <Button color="secondary" onClick={handleGT}>Confirm GT</Button>
                <Button color="primary" id="hidden" style={{visibility: updated ? 'visible' : 'hidden'}}onClick={handleUpload}>Upload to server</Button>
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
          disabled={pageNumber <= 1}
          onClick={previousPage}
        >
          Previous
        </Button>
        <Button
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