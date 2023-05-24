import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'
import { useState } from 'react'


function App(props:any) {

  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [idCounter, setIdCounter] = useState<number>(0);

  const handleId = () => {
    setIdCounter(idCounter + 1);
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
        <PDFevaluate onDisplayChange={handleDisplayChange}
         onload={getID}/>
      ) : (
        <Functions  onDisplayChange={handleDisplayChange}
         onload={getID} onChange={handleId}/>
      )}
    </Layout>
  )
}

export default App
