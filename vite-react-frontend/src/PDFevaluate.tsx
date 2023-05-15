import React, {useState} from 'react'
import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import axios from 'axios';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import mypdf from './assets/tempPdf.pdf'
import './PDFevaluate.css'
import 'bootstrap/dist/css/bootstrap.min.css';


import Functions from './Functions';
import { Button } from 'reactstrap';



const PDFevaluate = (props: any) => {

const [numPages, setNumPages] = useState(null);
const [pageNumber, setPageNumber] = useState(1);
const [pdf, setPdf] = useState(null);
const [gt, setGt] = useState(null);
var counter = 0; //Counts the number of documents that have been evaluated

//Function that will get the json object from backend using a get method with axios where the id is equal to counter
 const getJson = async () => { 
    const response = await axios.get("http://localhost:8000/getJson"+"?id="+counter);
    const data = await response.data;
    setPdf(data.PDF);
    setGt(data.GT);
 }

 //function that deletes the json object from the database where the id is equal to counter
const deleteJson = async () => {
  const response = await axios.delete("http://localhost:8000/deleteJson"+"?id="+counter);
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

return (
<div className='container'>
  <div className='heading'><h4>Verify the synthesized documents <span id='1'>({counter+1}/10)</span></h4></div> 
    <div className='row justify-content-center'>
      <div className='col-4'>
        <h5>Ground Truth JSON</h5>
        <pre>{gt}</pre>
      </div>
      <div className='col-1'><Button className="rounded-circle" color="danger" outline>&#10007;</Button></div>
      <div className='col-6'>
        <div className='pdfview'>
            <Document file={pdf} onLoadSuccess={onDocumentLoadSuccess}>
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