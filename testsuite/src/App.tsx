import './App.css'
import Layout from './Layout'
import Functions from './Functions'
import PDFevaluate from './PDFevaluate'


function App() {
  
//Functions/ skal være inni Layout muligens få med props fra children for å evaluere hva som vises
  return (
    <Layout>
      <Functions/>
    </Layout>
  )
}

export default App
