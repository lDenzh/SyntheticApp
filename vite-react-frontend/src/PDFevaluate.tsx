import React, {useEffect, useState} from 'react'
import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import axios from 'axios';
import JSZip from 'jszip';
import FileSaver from 'file-saver';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import mypdf from './assets/tempPdf.pdf'
import './PDFevaluate.css'
import 'bootstrap/dist/css/bootstrap.min.css';


import Functions from './Functions';
import { Button } from 'reactstrap';



const PDFevaluate = (props: any) => {

  interface BackendResponse {
    data: {
      received: boolean;
      message: {
        PDF: string;
        GT: string;
      }
    }
  }

const [numPages, setNumPages] = useState(null);
const [pageNumber, setPageNumber] = useState(1);
const [pdf, setPdf] = useState("");
const [gt, setGt] = useState("");
var counter = 1; //Counts the number of documents that have been evaluated
isLoading();
//Function that will get the json object from backend using a get method with axios where the id is equal to counter
 const getJson = async () => { 
    try {
      //get the json object from backend using a get method with axios where the id is equal to counter
      
      let response:BackendResponse = await axios.get("http://localhost:8000/documents/"+counter);

      var b64PDF = response.data.message.PDF; //decode the pdf from double-encoded base64 to base64-string 
      setPdf(b64PDF); //set the pdf state to the pdf from the json object
      setGt(response.data.message.GT);
      //set the pdf and gt state to the pdf and gt from the json object
      
    } catch(error:any) {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
    } else if (error.request) {
      // The request was made but no response was received
      // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
      // http.ClientRequest in node.js
      console.log(error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.log('Error', error.message);
    }
    console.log(error.config);
  };
    
 }

 //function that deletes the json object from the database where the id is equal to counter
const deleteJson = async () => {
  const response = await axios.delete("http://localhost:8000/documents/"+counter);
  const data = await response.data;
  console.log(data);
}
 getJson(); //displays the first document when the page is loaded

//Function that will get the next document to evaluate
const nextDoc = () => {
  counter++;
  getJson();
}
//Function that will delete the current document and get the next document to evaluate
const deleteDoc = () => {
  deleteJson();
  counter++;
  getJson();
}


function onDocumentLoadSuccess({ numPages }) {
  setNumPages(numPages);
}

let sampleGT:string = '[{\n   "label": "Navn",\n   "value": "Navn Navnesen"\n  },\n  {\n   "label": "Totalsum",\n   "value": "528.00 kr"\n  },\n  {\n   "label": "Telefon",\n   "value": "+4794721323"\n  }\n]';

async function downloadDocumentsAsZip(): Promise<void> {
  try {
    // Fetch all documents from the database using Axios
    const response = await axios.get('http://localhost:8000/documents');

    // Create a new JSZip instance
    const zip = new JSZip();

    // Add each document to the zip file
    response.data.forEach((document: any) => {
      // Decode the base64-encoded PDF to a Uint8Array
      const pdfData = Uint8Array.from(atob(document.pdf), c => c.charCodeAt(0));
      // Add the PDF to the zip file
      zip.file(`${document.id}.pdf`, pdfData);
      // Add the JSON data to the zip file
      zip.file(`${document.id}.json`, JSON.stringify(document.json));
    });

    // Generate the zip file as a Blob
    const blob = await zip.generateAsync({ type: 'blob' });

    // Save the zip file to the user's computer using FileSaver.js
    FileSaver.saveAs(blob, 'documents.zip');
  } catch (error) {
    console.error(error);
  }
}

const [loading, setLoading] = useState(true);
function isLoading() {
  
  useEffect(() => {
    const timoutID = setTimeout(() => setLoading(false), 6000);
    return () => clearTimeout(timoutID);
}, []);
}

if (loading) {
  return <div className='spinner-container'><div className="lds-ripple"><div></div><div></div></div></div>;
} if(!loading) return (
<div className='container'>
  <div className='heading'><h4>Verify the synthesized documents <span id='1'>({counter+1}/10)</span></h4></div> 
    <div className='row justify-content-center'>
      <div className='col-4'>
        <h5>Ground Truth JSON</h5>
        <pre>{gt}</pre>
        <Button color="primary" onClick={downloadDocumentsAsZip} outline>Download all files;</Button>
      </div>
      <div className='col-1'><Button className="rounded-circle" color="danger" onClick={deleteDoc} outline>&#10007;</Button></div>
      <div className='col-6'>
        <div className='pdfview'>
            <Document file={`data:application/pdf;base64,${pdf}`} onLoadSuccess={onDocumentLoadSuccess}>
              <Page pageNumber={pageNumber} />
            </Document>
        </div>
          <p>
            Page {pageNumber} of {numPages}
          </p>
        </div>
        <div className='col-1'><Button className="rounded-circle" color="success" onClick={nextDoc} outline>&#10003;</Button></div>
      </div>
    </div>
);
}

export default PDFevaluate