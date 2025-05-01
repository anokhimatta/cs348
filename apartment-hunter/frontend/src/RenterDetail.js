import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { getRenter, deleteRenter, getRenterApplications } from './apiService';
import './Renters.css';

const RenterDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [renter, setRenter] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const fetchRenterData = async () => {
      try {
        const renterData = await getRenter(id);
        setRenter(renterData);
        
        // Fetch renter's applications if available
        try {
          const applicationsData = await getRenterApplications(id);
          setApplications(applicationsData);
        } catch (appErr) {
          // Applications might not exist but we still want to show the renter details
          console.log('No applications found or error fetching them:', appErr);
          setApplications([]);
        }
        
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchRenterData();
  }, [id]);

  const handleDeleteClick = () => {
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteRenter(id);
      navigate('/renters');
    } catch (err) {
      setError(err.message);
      setShowDeleteConfirm(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
  };

  if (loading) return <div className="loading">Loading renter details...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!renter) return <div className="not-found">Renter not found</div>;

  return (
    <div className="renter-detail">
      <div className="page-header">
        <h1>Renter Details</h1>
        <div className="header-actions">
          <Link to="/renters" className="button-back">
            Back to List
          </Link>
          <Link to={`/renters/${id}/edit`} className="button-edit">
            Edit
          </Link>
          <button onClick={handleDeleteClick} className="btn btn-secondary">
            Delete
          </button>
        </div>
      </div>

      <div className="detail-card">
        <h2>{renter.name}</h2>
        
        <div className="detail-row">
          <div className="detail-label">Email:</div>
          <div className="detail-value">
            <a href={`mailto:${renter.email}`}>{renter.email}</a>
          </div>
        </div>
        
        <div className="detail-row">
          <div className="detail-label">Phone:</div>
          <div className="detail-value">
            <a href={`tel:${renter.phone_number}`}>{renter.phone_number}</a>
          </div>
        </div>
        
        <div className="detail-row">
          <div className="detail-label">Budget Range:</div>
          <div className="detail-value">${renter.min_budget} - ${renter.max_budget}</div>
        </div>
        
        <div className="detail-row">
          <div className="detail-label">Credit Score:</div>
          <div className="detail-value">{renter.credit_score}</div>
        </div>
      </div>

      <div className="related-section">
        <h3>Lease Applications</h3>
        
        {applications.length === 0 ? (
          <p>No lease applications found for this renter.</p>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Property</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map(app => (
                  <tr key={app.application_id}>
                    <td>{app.property_name}</td>
                    <td>
                      <span className={`status-badge status-${app.status.toLowerCase()}`}>
                        {app.status}
                      </span>
                    </td>
                    <td className="actions">
                      <Link to={`/applications/${app.application_id}`} className="button-view">
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        <div className="actions-container">
          <Link to={`/applications/new?renter=${id}`} className="button-add">
            Add New Application
          </Link>
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="delete-modal">
          <div className="delete-modal-content">
            <h2>Confirm Delete</h2>
            <p>Are you sure you want to delete {renter.name}? This action cannot be undone.</p>
            {applications.length > 0 && (
              <div className="warning-message">
                Warning: This renter has {applications.length} active application(s). Deleting the renter will also delete all associated applications.
              </div>
            )}
            <div className="delete-modal-actions">
              <button 
                onClick={handleDeleteConfirm} 
                className="button-danger"
              >
                Delete
              </button>
              <button 
                onClick={handleDeleteCancel} 
                className="button-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RenterDetail;