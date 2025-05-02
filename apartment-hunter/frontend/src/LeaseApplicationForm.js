import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import './Renters.css';

const LeaseApplicationForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [formData, setFormData] = useState({
    app_renter_id: '',
    app_property_id: '',
    status: 'Pending'
  });
  
  const [renters, setRenters] = useState([]);
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [formErrors, setFormErrors] = useState({});
  
  // Fetch renters and properties for dropdowns
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch renters
        const rentersResponse = await fetch('http://localhost:5000/renters');
        if (!rentersResponse.ok) {
          throw new Error(`Failed to fetch renters: ${rentersResponse.status}`);
        }
        const rentersData = await rentersResponse.json();
        setRenters(rentersData);
        
        // Fetch properties
        const propertiesResponse = await fetch('http://localhost:5000/properties');
        if (!propertiesResponse.ok) {
          throw new Error(`Failed to fetch properties: ${propertiesResponse.status}`);
        }
        const propertiesData = await propertiesResponse.json();
        setProperties(propertiesData);
        
        // If in edit mode, fetch the application data
        if (isEditMode) {
          const applicationResponse = await fetch(`http://localhost:5000/applications/${id}`);
          if (!applicationResponse.ok) {
            throw new Error(`Failed to fetch application: ${applicationResponse.status}`);
          }
          const applicationData = await applicationResponse.json();
          setFormData({
            app_renter_id: applicationData.app_renter_id,
            app_property_id: applicationData.app_property_id,
            status: applicationData.status
          });
        }
      } catch (err) {
        setError(`Failed to load data: ${err.message}`);
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [id, isEditMode]);
  
  const validateForm = () => {
    const errors = {};
    if (!formData.app_renter_id) {
      errors.app_renter_id = 'Renter is required';
    }
    if (!formData.app_property_id) {
      errors.app_property_id = 'Property is required';
    }
    if (!formData.status) {
      errors.status = 'Status is required';
    }
    return errors;
  };
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const errors = validateForm();
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    
    setSubmitting(true);
    
    try {
      const url = isEditMode 
        ? `http://localhost:5000/applications/${id}`
        : 'http://localhost:5000/applications';
        
      const method = isEditMode ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
      }
      
      navigate('/applications');
    } catch (err) {
      setError(`Failed to ${isEditMode ? 'update' : 'create'} application: ${err.message}`);
      console.error('Error submitting form:', err);
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="loader-container">
        <div className="loader"></div>
      </div>
    );
  }
  
  return (
    <div className="renter-form">
      <div className="page-header">
        <h1>{isEditMode ? 'Edit Lease Application' : 'Create Lease Application'}</h1>
      </div>
      
      {error && (
        <div className="alert alert-danger">
          {error}
        </div>
      )}
      
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="app_renter_id">Renter:</label>
            <select 
              id="app_renter_id"
              name="app_renter_id"
              value={formData.app_renter_id}
              onChange={handleInputChange}
              className={formErrors.app_renter_id ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">Select a Renter</option>
              {renters.map((renter) => (
                <option key={renter.renter_id} value={renter.renter_id}>
                  {renter.name} - Budget: ${renter.min_budget} to ${renter.max_budget}
                </option>
              ))}
            </select>
            {formErrors.app_renter_id && (
              <div className="error-text">{formErrors.app_renter_id}</div>
            )}
          </div>
          
          <div className="form-group">
            <label htmlFor="app_property_id">Property:</label>
            <select 
              id="app_property_id"
              name="app_property_id"
              value={formData.app_property_id}
              onChange={handleInputChange}
              className={formErrors.app_property_id ? 'error' : ''}
              disabled={submitting}
            >
              <option value="">Select a Property</option>
              {properties.map((property) => (
                <option key={property.property_id} value={property.property_id}>
                  {property.property_name} - ${property.price_per_person}/person - {property.num_bedrooms} beds, {property.num_bathrooms} baths
                </option>
              ))}
            </select>
            {formErrors.app_property_id && (
              <div className="error-text">{formErrors.app_property_id}</div>
            )}
          </div>
          
          <div className="form-group">
            <label htmlFor="status">Status:</label>
            <select 
              id="status"
              name="status"
              value={formData.status}
              onChange={handleInputChange}
              className={formErrors.status ? 'error' : ''}
              disabled={submitting}
            >
              <option value="PENDING">PENDING</option>
              <option value="APPROVED">APPROVED</option>
              <option value="DENIED">DENIED</option>
              <option value="WITHDRAWN">WITHDRAWN</option>
            </select>
            {formErrors.status && (
              <div className="error-text">{formErrors.status}</div>
            )}
          </div>
          
          <div className="form-actions">
            <Link to="/applications" className="btn btn-secondary">
              Cancel
            </Link>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={submitting}
            >
              {submitting ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LeaseApplicationForm;