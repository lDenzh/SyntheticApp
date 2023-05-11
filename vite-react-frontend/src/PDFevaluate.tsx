import React, {useState} from 'react'
import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import mypdf from './assets/SampleInvoice.pdf'
import './PDFevaluate.css'
import 'bootstrap/dist/css/bootstrap.min.css';


import Functions from './Functions';
import { Button } from 'reactstrap';



const PDFevaluate = (props: any) => {

const [numPages, setNumPages] = useState(null);
const [pageNumber, setPageNumber] = useState(1);

function getDocuments() {
  var count = 0;
  while (count < 10) {
    
  }
  return [
    { id: 1, name: 'SampleInvoice.pdf', url: mypdf },
  ];
}

function onDocumentLoadSuccess({ numPages }) {
  setNumPages(numPages);
}

let sampleGT:string = '[{\n   "label": "Navn",\n   "value": "Navn Navnesen"\n  },\n  {\n   "label": "Totalsum",\n   "value": "528.00 kr"\n  },\n  {\n   "label": "Telefon",\n   "value": "+4794721323"\n  }\n]';

return (
<div className='container'>
  <div className='heading'><h4>Verify the synthesized documents <span id='1'>(1/10)</span></h4></div> 
    <div className='row justify-content-center'>
      <div className='col-4'>
        <h5>Ground Truth JSON</h5>
        <pre>{sampleGT}</pre>
      </div>
      <div className='col-1'><Button className="rounded-circle" color="danger" outline>&#10007;</Button></div>
      <div className='col-6'>
        <div className='pdfview'>
            <Document file={file} onLoadSuccess={onDocumentLoadSuccess}>
              <Page pageNumber={pageNumber} />
            </Document>
        </div>
          <p>
            Page {pageNumber} of {numPages}
          </p>
        </div>
        <div className='col-1'><Button className="rounded-circle" color="success" outline>&#10003;</Button></div>
      </div>
    </div>
);
}

export default PDFevaluate