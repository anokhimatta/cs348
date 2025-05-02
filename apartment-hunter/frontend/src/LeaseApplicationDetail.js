import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import './Renters.css';

const LeaseApplicationDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [statusUpdateModal, setStatusUpdateModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [updateMessage, setUpdateMessage] = useState(null);

  useEffect(() => {
    const fetchApplicationDetail = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:5000/applications/${id}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setApplication(data);
        setNewStatus(data.status); // Initialize status with current value
        setError(null);
      } catch (err) {
        setError('Failed to fetch application details. Please try again later.');
        console.error('Error fetching application details:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchApplicationDetail();
  }, [id]);
  
  const handleDelete = async () => {
    try {
      const response = await fetch(`http://localhost:5000/applications/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      navigate('/applications');
    } catch (err) {
      setError('Failed to delete application. Please try again later.');
      console.error('Error deleting application:', err);
      setShowDeleteModal(false);
    }
  };
  
  const handleStatusUpdate = async () => {
    try {
      const response = await fetch(`http://localhost:5000/applications/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      // Update the local state with the new status
      setApplication(prev => ({ ...prev, status: newStatus }));
      setUpdateMessage('Status updated successfully!');
      
      // Hide message after 3 seconds
      setTimeout(() => {
        setUpdateMessage(null);
      }, 3000);
      
      setStatusUpdateModal(false);
    } catch (err) {
      setError('Failed to update status. Please try again later.');
      console.error('Error updating status:', err);
      setStatusUpdateModal(false);
    }
  };
  
  // Status badge styles
  const getStatusBadgeClass = (status) => {
    switch(status?.toLowerCase()) {
      case 'approved':
        return 'status-badge status-open';
      case 'pending':
        return 'status-badge status-inprogress';
      case 'rejected':
        return 'status-badge status-rejected';
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
  
  if (!application) {
    return (
      <div className="alert alert-danger">
        Application not found.
      </div>
    );
  }
  
  return (
    <div className="renter-detail">
      <div className="page-header">
        <h1>Lease Application Details</h1>
        <div className="header-actions">
          <button 
            className="btn btn-primary" 
            onClick={() => setStatusUpdateModal(true)}
          >
            Update Status
          </button>
          <Link to={`/applications/${id}/edit`} className="btn btn-secondary">
            Edit Application
          </Link>
          <button 
            className="btn btn-danger" 
            onClick={() => setShowDeleteModal(true)}
          >
            Delete
          </button>
        </div>
      </div>
      
      {updateMessage && (
        <div className="alert alert-success">
          {updateMessage}
        </div>
      )}
      
      <div className="detail-card">
        <div className="detail-row">
          <div className="detail-label">Application ID:</div>
          <div className="detail-value">{application.application_id}</div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Renter:</div>
          <div className="detail-value">
            <Link to={`/renters/${application.app_renter_id}`}>
              {application.renter_name}
            </Link>
          </div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Property:</div>
          <div className="detail-value">
            <Link to={`/properties/${application.app_property_id}`}>
              {application.property_name}
            </Link>
          </div>
        </div>
        <div className="detail-row">
          <div className="detail-label">Status:</div>
          <div className="detail-value">
            <span className={getStatusBadgeClass(application.status)}>
              {application.status}
            </span>
          </div>
        </div>
      </div>
      
      <div className="actions-container">
        <Link to="/applications" className="btn btn-secondary">
          Back to Applications
        </Link>
      </div>
      
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Confirm Delete</h3>
              <button 
                className="close-button" 
                onClick={() => setShowDeleteModal(false)}
              >
                &times;
              </button>
            </div>
            <p>Are you sure you want to delete this application? This action cannot be undone.</p>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowDeleteModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-danger" 
                onClick={handleDelete}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Status Update Modal */}
      {statusUpdateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Update Application Status</h3>
              <button 
                className="close-button" 
                onClick={() => setStatusUpdateModal(false)}
              >
                &times;
              </button>
            </div>
            <div className="form-group">
              <label htmlFor="status">Status:</label>
              <select
                id="status"
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="search-input"
              >
                <option value="Pending">Pending</option>
                <option value="Approved">Approved</option>
                <option value="Rejected">Rejected</option>
                <option value="Withdrawn">Withdrawn</option>
              </select>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary" 
                onClick={() => setStatusUpdateModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleStatusUpdate}
              >
                Update
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LeaseApplicationDetail;