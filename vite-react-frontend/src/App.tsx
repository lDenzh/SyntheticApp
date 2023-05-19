import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'
import { useState } from 'react'


function App(props:any) {

  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [idCounter, setIdCounter] = useState<number>(1);

  const handleId = (value:any) => {
    setIdCounter(value);
  };

  const getID = () => {
    return idCounter;
  }
  
  const handleDisplayChange = (value:any) => {
    setUploadSuccess(value);
  };


  return (
    <Layout>
      {uploadSuccess ? (
        <PDFevaluate onDisplayChange={handleDisplayChange} onChange={getID}/>
      ) : (
        <Functions  onDisplayChange={handleDisplayChange} onChange={handleId}  />
      )}
    </Layout>
  )
}

export default App
