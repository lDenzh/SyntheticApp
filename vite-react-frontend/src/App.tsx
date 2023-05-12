import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'
import { useState } from 'react'


function App(props:any) {

  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [retrievedJSON, setRetrievedJSON] = useState(false);
  const handleDisplayChange = (value:any) => {
    setUploadSuccess(value);
  };

  const handleRetrievedJSON  = (value:any) => {
    setRetrievedJSON(value);
  };
  

  return (
    <Layout>
      {uploadSuccess ? (
        <PDFevaluate fileProp={retrievedJSON} onDisplayChange={handleDisplayChange}/>
      ) : (
        <Functions onUploadChange={handleRetrievedJSON} onDisplayChange={handleDisplayChange} />
      )}
    </Layout>
  )
}

export default App
