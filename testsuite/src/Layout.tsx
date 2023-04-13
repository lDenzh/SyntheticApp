import React from 'react'
import Navigation from './Navigation'

 function Layout(props) {
  return (
    <div className={props.class}>
        <Navigation/>
        <hr/>
        {props.children}
        <hr/>
        <p>© 2023 Robocar. No rights reserved</p>
    </div>
  )
}

export default Layout
