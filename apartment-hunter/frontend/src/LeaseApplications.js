import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Renters.css'; // Using the same CSS file as Renters

const LeaseApplications = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  
  // Search and filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Fetch applications
  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/applications');
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setApplications(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch applications. Please try again later.');
        console.error('Error fetching applications:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchApplications();
  }, []);
  
  // Handle navigation functions
  const handleAddNew = () => navigate('/applications/new');
  const handleView = (id) => navigate(`/applications/${id}`);
  //const handleEdit = (id) => navigate(`/applications/${id}/edit`);
  
  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };
  
  // Handle status filter change
  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
  };
  
  // Filter applications based on search term and status
  const filteredApplications = applications.filter(app => {
    const matchesSearch = 
      app.renter_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
      app.property_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.status?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === '' || app.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });
  
  const currentItems = filteredApplications;
  
  // Get unique status values for filter dropdown
  const statusOptions = [...new Set(applications.map(app => app.status))];
  
  // Status badge styles
  const getStatusBadgeClass = (status) => {
    switch(status?.toLowerCase()) {
      case 'approved':
        return 'status-badge status-open';
      case 'pending':
        return 'status-badge status-inprogress';
      case 'denied':
        return 'status-badge status-denied';
      case 'withdrawn':
        return 'status-badge status-closed';
      default:
        return 'status-badge status-new';
    }
  };
  
  if (loading) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="alert alert-danger">
        {error}
      </div>
    );
  }
  
  return (
    <div className="renter-list">
      <div className="page-header">
        <h1>Lease Applications</h1>
        <div className="header-actions">
          <button onClick={handleAddNew} className="btn btn-primary">Add New Application</button>
        </div>
      </div>
      
      {/* Search and Filters */}
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by renter or property name..."
            className="search-input"
            value={searchTerm}
            onChange={handleSearchChange}
          />
        </div>
        <div className="filter-row">
          <div className="filter-item">
            <label htmlFor="status-filter">Filter by Status:</label>
            <select
              id="status-filter"
              className="search-input"
              value={statusFilter}
              onChange={handleStatusFilterChange}
            >
              <option value="">All Statuses</option>
              {statusOptions.map((status, index) => (
                <option key={index} value={status}>{status}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Applications Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Renter</th>
              <th>Property</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currentItems.length > 0 ? (
              currentItems.map((application) => (
                <tr key={application.application_id}>
                  <td>{application.application_id}</td>
                  <td>{application.renter_name}</td>
                  <td>{application.property_name}</td>
                  <td>
                    <span className={getStatusBadgeClass(application.status)}>
                      {application.status}
                    </span>
                  </td>
                  <td className="action-icons">
                    <button 
                      onClick={() => handleView(application.application_id)} 
                      className="btn btn-info btn-sm" 
                      title="View Details"
                    >
                      View
                    </button>
                    {' '}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center' }}>
                  No applications found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination 
      {filteredApplications.length > itemsPerPage && (
        <div className="pagination">
          <button
            onClick={() => paginate(currentPage - 1)}
            disabled={currentPage === 1}
            className="pagination-button"
          >
            Previous
          </button>
          
          {Array.from({ length: Math.ceil(filteredApplications.length / itemsPerPage) }, (_, i) => (
            <button
              key={i}
              onClick={() => paginate(i + 1)}
              className={`pagination-button ${currentPage === i + 1 ? 'active' : ''}`}
            >
              {i + 1}
            </button>
          ))}
          
          <button
            onClick={() => paginate(currentPage + 1)}
            disabled={currentPage === Math.ceil(filteredApplications.length / itemsPerPage)}
            className="pagination-button"
          >
            Next
          </button>
        </div>
      )}*/}
    </div>
  );
};

export default LeaseApplications;