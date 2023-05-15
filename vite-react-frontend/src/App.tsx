import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'
import { useState } from 'react'


function App(props:any) {

  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  const handleDisplayChange = (value:any) => {
    setUploadSuccess(value);
  };


  return (
    <Layout>
      {uploadSuccess ? (
        <PDFevaluate onDisplayChange={handleDisplayChange}/>
      ) : (
        <Functions  onDisplayChange={handleDisplayChange} />
      )}
    </Layout>
  )
}

export default App
