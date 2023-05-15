
import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import {
    Collapse,
    Navbar,
    NavbarToggler,
    NavbarBrand,
    Nav,
    NavItem,
    NavLink,
  } from 'reactstrap';

const Navigation = () => {
    const [collapsed, setCollapsed] = useState(true);
    const toggleNavbar = () => setCollapsed(!collapsed);

    const navbarStyle = {
      width:'1280px', margin: '20px 0 0 0'

    }

  return (
    <div style={navbarStyle}>
      <Navbar color="faded" light>
        <NavbarBrand href="/" className="me-auto">
          Document Synthesizer
        </NavbarBrand>
        <NavbarToggler onClick={toggleNavbar} className="me-2" />
        <Collapse isOpen={!collapsed} navbar>
          <Nav navbar>
            <NavItem>
              <NavLink href="/components/">Documents</NavLink>
            </NavItem>
            <NavItem>
              <NavLink href="https://www.cradl.ai/use-cases/invoice-ocr-api">Cradl.ai</NavLink>
            </NavItem>
            <NavItem>
              <NavLink href="https://github.com/LucidtechAI/synthetic">
                GitHub
              </NavLink>
            </NavItem>
          </Nav>
        </Collapse>
      </Navbar>
      <hr/>
    </div>
  );
}

export default Navigation