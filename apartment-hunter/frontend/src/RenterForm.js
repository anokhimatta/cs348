import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getRenter, createRenter, updateRenter } from './apiService';
import './Renters.css';

const RenterForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    min_budget: '',
    max_budget: '',
    credit_score: ''
  });
  
  const [loading, setLoading] = useState(isEditMode);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});

  useEffect(() => {
    const fetchRenter = async () => {
      if (isEditMode) {
        try {
          const data = await getRenter(id);
          setFormData({
            name: data.name || '',
            email: data.email || '',
            phone_number: data.phone_number || '',
            min_budget: data.min_budget || '',
            max_budget: data.max_budget || '',
            credit_score: data.credit_score || ''
          });
          setLoading(false);
        } catch (err) {
          setError(err.message);
          setLoading(false);
        }
      }
    };

    fetchRenter();
  }, [id, isEditMode]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear validation error when field is edited
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    }
    
    if (!formData.email.trim()) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }
    
    if (!formData.phone_number.trim()) {
      errors.phone_number = 'Phone number is required';
    }
    
    if (!formData.min_budget) {
      errors.min_budget = 'Minimum budget is required';
    } else if (isNaN(formData.min_budget) || Number(formData.min_budget) < 0) {
      errors.min_budget = 'Minimum budget must be a positive number';
    }
    
    if (!formData.max_budget) {
      errors.max_budget = 'Maximum budget is required';
    } else if (isNaN(formData.max_budget) || Number(formData.max_budget) < 0) {
      errors.max_budget = 'Maximum budget must be a positive number';
    } else if (Number(formData.max_budget) < Number(formData.min_budget)) {
      errors.max_budget = 'Maximum budget must be greater than minimum budget';
    }
    
    if (!formData.credit_score) {
      errors.credit_score = 'Credit score is required';
    } else if (isNaN(formData.credit_score) || Number(formData.credit_score) < 300 || Number(formData.credit_score) > 850) {
      errors.credit_score = 'Credit score must be between 300 and 850';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setSubmitting(true);
      setError(null);
      
      const numericFormData = {
        ...formData,
        min_budget: Number(formData.min_budget),
        max_budget: Number(formData.max_budget),
        credit_score: Number(formData.credit_score)
      };
      
      if (isEditMode) {
        await updateRenter(id, numericFormData);
        navigate(`/renters/${id}`);
      } else {
        // For new renter, generate a unique ID
        const renterWithId = {
          ...numericFormData,
          renter_id: Date.now()  // Simple unique ID for demonstration
        };
        await createRenter(renterWithId);
        navigate('/renters');
      }
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  if (loading) return <div className="loading">Loading renter data...</div>;

  return (
    <div className="renter-form">
      <div className="page-header">
        <h1>{isEditMode ? 'Edit Renter' : 'Add New Renter'}</h1>
        <Link to={isEditMode ? `/renters/${id}` : '/renters'} className="button-back">
          Cancel
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="form-container">
        <div className="form-group">
          <label htmlFor="name">Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className={validationErrors.name ? 'error' : ''}
          />
          {validationErrors.name && <div className="error-text">{validationErrors.name}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className={validationErrors.email ? 'error' : ''}
          />
          {validationErrors.email && <div className="error-text">{validationErrors.email}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="phone_number">Phone Number</label>
          <input
            type="tel"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            className={validationErrors.phone_number ? 'error' : ''}
          />
          {validationErrors.phone_number && <div className="error-text">{validationErrors.phone_number}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="min_budget">Minimum Budget ($)</label>
          <input
            type="number"
            id="min_budget"
            name="min_budget"
            value={formData.min_budget}
            onChange={handleChange}
            min="0"
            className={validationErrors.min_budget ? 'error' : ''}
          />
          {validationErrors.min_budget && <div className="error-text">{validationErrors.min_budget}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="max_budget">Maximum Budget ($)</label>
          <input
            type="number"
            id="max_budget"
            name="max_budget"
            value={formData.max_budget}
            onChange={handleChange}
            min="0"
            className={validationErrors.max_budget ? 'error' : ''}
          />
          {validationErrors.max_budget && <div className="error-text">{validationErrors.max_budget}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="credit_score">Credit Score</label>
          <input
            type="number"
            id="credit_score"
            name="credit_score"
            value={formData.credit_score}
            onChange={handleChange}
            min="300"
            max="850"
            className={validationErrors.credit_score ? 'error' : ''}
          />
          {validationErrors.credit_score && <div className="error-text">{validationErrors.credit_score}</div>}
        </div>

        <div className="form-actions">
          <button 
            type="submit" 
            className="button-primary" 
            disabled={submitting}
          >
            {submitting ? 'Saving...' : (isEditMode ? 'Update Renter' : 'Add Renter')}
          </button>
          <Link to={isEditMode ? `/renters/${id}` : '/renters'} className="button-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
};

export default RenterForm;