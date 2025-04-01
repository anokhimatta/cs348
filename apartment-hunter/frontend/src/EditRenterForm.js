import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getRenter, updateRenter } from './apiService.js';
import './Renters.css';

const EditRenterForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    min_budget: '',
    max_budget: '',
    credit_score: ''
  });

  // Load renter data when component mounts
  useEffect(() => {
    const fetchRenter = async () => {
      try {
        setLoading(true);
        const data = await getRenter(id);
        setFormData({
          name: data.name,
          email: data.email,
          phone_number: data.phone_number,
          min_budget: data.min_budget,
          max_budget: data.max_budget,
          credit_score: data.credit_score
        });
        setError(null);
      } catch (err) {
        setError('Failed to load renter data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRenter();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name || !formData.email || !formData.phone_number) {
      setError('Please fill in all required fields');
      return;
    }
    
    try {
      await updateRenter(id, formData);
      navigate(`/renters/${id}`);
    } catch (err) {
      setError('Failed to update renter');
      console.error(err);
    }
  };

  if (loading) {
    return <div className="loading">Loading renter data...</div>;
  }

  return (
    <div className="renter-form-container">
      <h2>Edit Renter</h2>
      
      {error && <div className="error-message">{error}</div>}
      
      <form onSubmit={handleSubmit} className="renter-form">
        <div className="form-group">
          <label htmlFor="name">Name*</label>
          <input 
            type="text" 
            id="name" 
            name="name" 
            value={formData.name} 
            onChange={handleChange} 
            required 
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email*</label>
          <input 
            type="email" 
            id="email" 
            name="email" 
            value={formData.email} 
            onChange={handleChange} 
            required 
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="phone_number">Phone Number*</label>
          <input 
            type="tel" 
            id="phone_number" 
            name="phone_number" 
            value={formData.phone_number} 
            onChange={handleChange} 
            required 
          />
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="min_budget">Minimum Budget ($)</label>
            <input 
              type="number" 
              id="min_budget" 
              name="min_budget" 
              value={formData.min_budget} 
              onChange={handleChange} 
              min="0"
            />
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
            />
          </div>
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
          />
        </div>
        
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate(`/renters/${id}`)}>
            Cancel
          </button>
          <button type="submit" className="btn-primary">
            Update Renter
          </button>
        </div>
      </form>
    </div>
  );
};

export default EditRenterForm;