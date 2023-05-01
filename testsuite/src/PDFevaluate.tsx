import React, {useState} from 'react'
import { Document, Page } from 'react-pdf/dist/esm/entry.vite';
import "react-pdf/dist/esm/Page/TextLayer.css";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import mypdf from './assets/SampleInvoice.pdf'
import './PDFevaluate.css'
import 'bootstrap/dist/css/bootstrap.min.css';


import Functions from './Functions';
import { Button } from 'reactstrap';



const PDFevaluate = () => {


const [numPages, setNumPages] = useState(null);
const [pageNumber, setPageNumber] = useState(1);

function onDocumentLoadSuccess({ numPages }) {
  setNumPages(numPages);
}


return (
<div className='container'>
    <div className='row justify-content center'>
      <div className='col-4'>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>
        <p>a ground truth or something</p>

      </div>
      
      <div className='col-4'>
        <div className='pdfview'>
          <Button className="rounded-circle" color="danger">X</Button>
            <Document file={mypdf} onLoadSuccess={onDocumentLoadSuccess}>
              <Page pageNumber={pageNumber} />
            </Document>
          <Button className="rounded-circle" color="success">V</Button>
        </div>
          <p>
            Page {pageNumber} of {numPages}
          </p>
          
        </div>
      </div>
    </div>
);
}

export default PDFevaluate