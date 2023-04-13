import React, { useRef, useState } from "react";
import './App.css'
import axios, { isAxiosError } from 'axios';

import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import eksempelpdf from "./pdf.pdf";


const App = () => {
    const [file, setFile] = useState();
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

        const { data } = await axios.post("http://localhost:8000/runSynth", payload, {
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json'
              },
              
        })
        console.log(data);
        // muligens gjøre setFile = data; for å vise resultatet.
    }

    const handleUpload = () => {
        Postman();
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
                    placeholder='    {
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
                <button onClick={() => setFile(null)}>Cancel</button>
                <button onClick={handleGT}>Confirm GT</button>
                <button id="hidden" onClick={handleUpload}>Upload to server</button>
        </div>
      <div style={{marginLeft: "120px"}}>
        <Document
            file={file[0]}
            onLoadSuccess={onDocumentLoadSuccess}>
          <Page pageNumber={pageNumber} renderTextLayer={false}/>
        </Document>
              <div>
      <p>
        Page {pageNumber || (numPages ? 1 : '--')} of {numPages || '--'}
      </p>
      <button
        type="button"
        disabled={pageNumber <= 1}
        onClick={previousPage}
      >
        Previous
      </button>
      <button
        type="button"
        disabled={pageNumber >= numPages}
        onClick={nextPage}
      >
        Next
      </button>
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
                <h1>Drag and drop PDF to upload</h1>
                <h1>or select PDF from file explorer</h1>
                <input
                    type = 'file'
                    accept= 'application/pdf'
                    onChange={(event) => setFile(event.target.files)}
                    hidden
                    ref = {inputRef}
                />
                <button onClick = {() => inputRef.current.click()} className="button">Choose file</button>
            </div>
            )}
        </>
    )
}

export default App;