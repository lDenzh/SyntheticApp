import React, {useEffect, useState} from 'react'
import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import axios from 'axios';
import JSZip from 'jszip';
import FileSaver from 'file-saver';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import './PDFevaluate.css'
import 'bootstrap/dist/css/bootstrap.min.css';
import { Button } from 'reactstrap';


const PDFevaluate = (props: any) => {
  const [numPages, setNumPages] = useState<any | number>(null);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [pdf, setPdf] = useState("");
  const [gt, setGt] = useState("");
  const [counter, setCounter] = useState<number>(1);
  const [showButton, setShowButton] = useState<boolean>(true);
  var orgID = props.onload();

  interface BackendResponse {
    data: {
      received: boolean;
      message: {
        PDF: string;
        GT: {
          label: string;
          value: string;
        }
      }
    }
  }
  
  isLoading();
  //Displays the first document when the page is loaded the first time*
  useEffect(() => {
  fetchData();
  }, []); // Second argument is an empty array so that it only runs once
  
  //Function that will get the json object from backend using a get method with axios where the id is equal to counter
  const fetchData = async () => { 
    try {
      //get the json object from backend using a get method with axios where the id is equal to counter
      console.log("counter = "+counter);
      let response:BackendResponse = await axios.get("http://localhost:8000/documents/"+orgID+"/"+counter);
      
      var b64PDF = response.data.message.PDF; //decode the pdf from double-encoded base64 to base64-string 
      setPdf(b64PDF); //set the pdf state to the pdf from the json object
      setGt(JSON.stringify(response.data.message.GT));
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

//Function that will get the next document to evaluate
const nextDoc = () => {
  if (counter < 10){
    setCounter((counter) => counter + 1)
    fetchData();
  } else {
    console.log("no more docs to evaluate");
    setShowButton(false);
  }
}

//Function that will delete the current document and get the next document to evaluate
const deleteDoc = async () => {
  const response = await axios.delete("http://localhost:8000/documents/"+orgID+"/"+counter);
  const data = await response.data;
  console.log(data);
  console.log("deleted doc nr: "+counter);
  if (counter < 10){
    setCounter((counter) => counter + 1)
    fetchData();
  } else {
    console.log("no more docs to evaluate");
  }
}

function onDocumentLoadSuccess({ numPages }) {
  setNumPages(numPages);
}

async function downloadDocumentsAsZip(): Promise<void> {
  try {
    // Fetch all documents from the database using Axios
    const response = await axios.get('http://localhost:8000/documents/'+orgID);
    const pairsOfData = Object.values(await response.data.message);
    console.log(pairsOfData);
    console.log(typeof pairsOfData);
    console.log(Object.keys(pairsOfData))
    console.log(pairsOfData[1])
    
    // Create a new JSZip instance
    const zip = new JSZip();

    // Add each document to the zip file
    for (let pairKey of Object.keys(pairsOfData)) {
      const pair = pairsOfData[pairKey];
      var { PDF, GT } = pair // Destructure the properties from the current item

      // Decode the base64-encoded PDF to a Uint8Array
      const pdfData = Uint8Array.from(atob(PDF), (c) => c.charCodeAt(0));
      const gtData = JSON.stringify(GT);
    
      zip.file(`DocID${orgID}nr${pairKey}.pdf`, pdfData); // Add the PDF to the zip file
    
      zip.file(`DocID${orgID}nr${pairKey}.json`, gtData); // Add the JSON data to the zip file
    };

    // Generate the zip file as a Blob
    const blob = await zip.generateAsync({ type: 'blob' });

    // Save the zip file to the user's computer using FileSaver.js
    FileSaver.saveAs(blob, `documents${orgID}.zip`);
  } catch (error) {
    console.error(error);
  }
}

const [loading, setLoading] = useState(true);

function isLoading() {
  useEffect(() => {
    const timoutID = setTimeout(() => setLoading(false), 3000);
    return () => clearTimeout(timoutID);
}, []);
}

if (loading) {
  return <div className='spinner-container'><div className="lds-ripple"><div></div><div></div></div></div>;
} else return (
<div className='container'>
  <div className='heading'><h4>Verify the synthesized documents <span id='1'>({counter}/10) of {orgID}</span></h4></div> 
    <div className='row justify-content-center'>
      <div className='col-4'>
        <h5>Ground Truth JSON</h5>
        <p>{gt}</p>
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