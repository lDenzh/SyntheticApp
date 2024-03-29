import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'
import { useState } from 'react'


function App(props:any) {

  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [idCounter, setIdCounter] = useState<number>(1);

  const handleId = () => {
    setIdCounter(idCounter + 1);
    console.log("idCounter = "+idCounter);
  };

  const getID = () => {
    return idCounter;
  }
  
  const handleDisplayChange = (value:boolean) => {
    setUploadSuccess(value);
  
  };


  return (
    <Layout>
      {uploadSuccess ? (
        <PDFevaluate onDisplayChange={handleDisplayChange}
         onload={getID} onChange={handleId}/>
      ) : (
        <Functions  onDisplayChange={handleDisplayChange}
         onload={getID}/>
      )}
    </Layout>
  )
}

export default App
