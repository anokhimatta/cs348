import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RenterList from './RenterList.js';
import RenterForm from './RenterForm.js';
import RenterDetail from './RenterDetail.js';
import EditRenterForm from './EditRenterForm.js';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <h1>Apartment Rental Management</h1>
          <nav className="main-nav">
            <ul>
              <li><a href="/">Renters</a></li>
              {/* Add other nav links for Properties, Offices, etc. */}
            </ul>
          </nav>
        </header>
        
        <main className="app-content">
          <Routes>
            <Route path="/" element={<Navigate to="/renters" />} />
            <Route path="/renters" element={<RenterList />} />
            <Route path="/renters/new" element={<RenterForm />} />
            <Route path="/renters/:id" element={<RenterDetail />} />
            <Route path="/renters/:id/edit" element={<EditRenterForm />} />
          </Routes>
        </main>
        
        <footer className="app-footer">
          <p>© 2025 Apartment Hunter</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;