import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import RenterList from './RenterList.js';
import RenterForm from './RenterForm.js';
import RenterDetail from './RenterDetail.js';
import EditRenterForm from './EditRenterForm.js';
import Property from './Property.js';
import LeaseApplications from './LeaseApplications';
import LeaseApplicationDetail from './LeaseApplicationDetail';
import LeaseApplicationForm from './LeaseApplicationForm';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <header className="app-header">
          <h1>Apartment Rental Management</h1>
          <nav className="main-nav">
            <ul>
              <li><Link to="/renters">Renters</Link></li>
              <li><Link to="/properties">Properties</Link></li>
              <li><Link to="/applications">Lease Applications</Link></li>

              {/* Add other nav links for Offices, etc. */}
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
            
            {/* Add routes for Properties */}
            <Route path="/properties" element={<Property />} />
            {/* If you have separate components for property details, add them here */}
            {/* <Route path="/properties/new" element={<PropertyForm />} /> */}
            {/* <Route path="/properties/:id" element={<PropertyDetail />} /> */}
            {/* <Route path="/properties/:id/edit" element={<EditPropertyForm />} /> */}
            <Route path="/applications" element={<LeaseApplications />} />
            <Route path="/applications/:id" element={<LeaseApplicationDetail />} />
            <Route path="/applications/new" element={<LeaseApplicationForm />} />
            <Route path="/applications/:id/edit" element={<LeaseApplicationForm />} />
          </Routes>
        </main>
        
        <footer className="app-footer">
          <p>Apartment Hunter</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;