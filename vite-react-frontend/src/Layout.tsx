import Navigation from './Navigation'

 function Layout(props:any) {
  return (
    <div className={props.class}>
        <Navigation/>
        {props.children}
        <hr/>
        <p>© 2023 Lucidtech.ai</p>
    </div>
  )
}

export default Layout
