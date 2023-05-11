import React from 'react'
import ReactDOM from 'react-dom/client'
import FileUpload from './App'
import App from './App'
import './index.css'

import PDFevaluate from './PDFevaluate'
import Layout from './Layout'

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
      <PDFevaluate/>
  </React.StrictMode>,
)
