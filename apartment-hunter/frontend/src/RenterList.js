import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { getAllRenters, deleteRenter } from './apiService';
import './Renters.css';

const RenterList = () => {
  const [renters, setRenters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);

  useEffect(() => {
    const fetchRenters = async () => {
      try {
        const data = await getAllRenters();
        setRenters(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchRenters();
  }, []);

  const handleDeleteClick = (id) => {
    setDeleteConfirmId(id);
  };

  const handleDeleteConfirm = async (id) => {
    try {
      await deleteRenter(id);
      setRenters(renters.filter(renter => renter.renter_id.toString() !== id.toString()));
      setDeleteConfirmId(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmId(null);
  };

  const navigate = useNavigate();

  if (loading) return <div className="loading">Loading renters...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;

  return (
    <div className="renter-list">
      <div className="page-header">
        <h1>Renters</h1>
        <Link to="/renters/new" className="button-add">
          Add New Renter
        </Link>
      </div>

      {renters.length === 0 ? (
        <div className="empty-list">
          <p>No renters found. Click "Add New Renter" to create one.</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Budget Range</th>
                <th>Credit Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {renters.map(renter => (
                <tr key={renter.renter_id}>
                  <td>{renter.name}</td>
                  <td>{renter.email}</td>
                  <td>{renter.phone_number}</td>
                  <td>${renter.min_budget} - ${renter.max_budget}</td>
                  <td>{renter.credit_score}</td>
                  <td className="actions">
                    <button className="btn-container"
                      onClick={() => navigate(`/renters/${renter.renter_id}`)} 
                      /*className="button-view"*/
                    >
                      View
                    </button>

                    <button className="btn-container"
                      onClick={() => navigate(`/renters/${renter.renter_id}/edit`)} 
                      /*className="button-view"*/
                    >
                      Edit
                    </button>

                    <button className="btn-container" 
                      onClick={() => handleDeleteClick(renter.renter_id)} 
                      /*className="button-delete"*/
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {deleteConfirmId && (
        <div className="delete-modal">
          <div className="delete-modal-content">
            <h2>Confirm Delete</h2>
            <p>Are you sure you want to delete this renter? This action cannot be undone.</p>
            <div className="delete-modal-actions">
              <button 
                onClick={() => handleDeleteConfirm(deleteConfirmId)} 
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

export default RenterList;



/*<Link to={`/renters/${renter.renter_id}`} className="button-view">
                      View
                    </Link>
                    <Link to={`/renters/${renter.renter_id}/edit`} className="button-edit">
                      Edit
                    </Link>*/