import React, { useState, useEffect } from 'react';
import './Properties.css';

const PropertyList = () => {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProperty, setSelectedProperty] = useState(null);
  const [alertMessage, setAlertMessage] = useState(null);
  
  const [currentPage, setCurrentPage] = useState(1);
  const [propertiesPerPage] = useState(10);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [bedroomFilter, setBedroomFilter] = useState('');

  const fetchProperties = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/properties');
      const data = await response.json();
      setProperties(data);
    } catch (error) {
      console.error('Error fetching properties:', error);
      setAlertMessage({ type: 'danger', text: 'Failed to load properties' });
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchProperties();
  }, []);

  const handleDelete = async (propertyId) => {
    if (window.confirm('Are you sure you want to delete this property?')) {
      try {
        const response = await fetch(`http://localhost:5000/properties/${propertyId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          setAlertMessage({ type: 'success', text: 'Property deleted successfully' });
          fetchProperties();
        } else {
          const errorData = await response.json();
          setAlertMessage({ type: 'danger', text: `Failed to delete property: ${errorData.error}` });
        }
      } catch (error) {
        console.error('Error deleting property:', error);
        setAlertMessage({ type: 'danger', text: 'Failed to delete property' });
      }
    }
  };

  const handleViewDetails = (property) => {
    setSelectedProperty(property);
  };

  const handleEdit = (property) => {
    setSelectedProperty(property);
    setShowEditModal(true);
  };

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.property_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         property.address.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesBedrooms = bedroomFilter === '' || property.num_bedrooms.toString() === bedroomFilter;
    
    const matchesPrice = (minPrice === '' || property.price_per_person >= parseInt(minPrice)) && 
                         (maxPrice === '' || property.price_per_person <= parseInt(maxPrice));
    
    return matchesSearch && matchesBedrooms && matchesPrice;
  });

  const indexOfLastProperty = currentPage * propertiesPerPage;
  const indexOfFirstProperty = indexOfLastProperty - propertiesPerPage;
  const currentProperties = filteredProperties.slice(indexOfFirstProperty, indexOfLastProperty);
  const totalPages = Math.ceil(filteredProperties.length / propertiesPerPage);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);
  
  const resetFilters = () => {
    setSearchTerm('');
    setMinPrice('');
    setMaxPrice('');
    setBedroomFilter('');
  };

  return (
    <div className="property-list">
      <div className="page-header">
        <h1>Properties</h1>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
            Add New Property
          </button>
        </div>
      </div>
      
      {alertMessage && (
        <div className={`alert alert-${alertMessage.type}`}>
          {alertMessage.text}
        </div>
      )}
      
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            className="search-input"
            placeholder="Search by name or address..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-row">
          <div className="filter-item">
            <label>Bedrooms:</label>
            <select 
              value={bedroomFilter} 
              onChange={(e) => setBedroomFilter(e.target.value)}
              className="search-input"
            >
              <option value="">All</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4+</option>
            </select>
          </div>
          <div className="filter-item">
            <label>Min Price:</label>
            <input
              type="number"
              className="search-input"
              placeholder="Min price"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
            />
          </div>
          <div className="filter-item">
            <label>Max Price:</label>
            <input
              type="number"
              className="search-input"
              placeholder="Max price"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
            />
          </div>
          <button className="btn btn-secondary" onClick={resetFilters}>
            Reset Filters
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="loader-container">
          <div className="loader"></div>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Address</th>
                  <th>Bedrooms</th>
                  <th>Bathrooms</th>
                  <th>Price</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentProperties.length > 0 ? (
                  currentProperties.map(property => (
                    <tr key={property.property_id}>
                      <td>{property.property_id}</td>
                      <td>{property.property_name}</td>
                      <td>{property.address}</td>
                      <td>{property.num_bedrooms}</td>
                      <td>{property.num_bathrooms}</td>
                      <td>${property.price_per_person}</td>
                      <td className="action-icons">
                        <button 
                          className="icon-button view" 
                          onClick={() => handleViewDetails(property)}
                          title="View Details"
                        >
                          <i className="fas fa-eye"></i>
                        </button>
                        <button 
                          className="icon-button edit" 
                          onClick={() => handleEdit(property)}
                          title="Edit Property"
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button 
                          className="icon-button delete" 
                          onClick={() => handleDelete(property.property_id)}
                          title="Delete Property"
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" style={{ textAlign: 'center' }}>No properties found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Pagination */}
          {filteredProperties.length > propertiesPerPage && (
            <div className="pagination">
              <button 
                className="pagination-button" 
                onClick={() => paginate(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button
                  key={i + 1}
                  className={`pagination-button ${currentPage === i + 1 ? 'active' : ''}`}
                  onClick={() => paginate(i + 1)}
                >
                  {i + 1}
                </button>
              ))}
              <button 
                className="pagination-button" 
                onClick={() => paginate(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
      
      {/* Property Details Modal */}
      {selectedProperty && !showEditModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Property Details</h2>
              <button className="close-button" onClick={() => setSelectedProperty(null)}>×</button>
            </div>
            <div className="detail-card">
              <div className="detail-row">
                <div className="detail-label">Property ID:</div>
                <div className="detail-value">{selectedProperty.property_id}</div>
              </div>
              <div className="detail-row">
                <div className="detail-label">Property Name:</div>
                <div className="detail-value">{selectedProperty.property_name}</div>
              </div>
              <div className="detail-row">
                <div className="detail-label">Address:</div>
                <div className="detail-value">{selectedProperty.address}</div>
              </div>
              <div className="detail-row">
                <div className="detail-label">Bedrooms:</div>
                <div className="detail-value">{selectedProperty.num_bedrooms}</div>
              </div>
              <div className="detail-row">
                <div className="detail-label">Bathrooms:</div>
                <div className="detail-value">{selectedProperty.num_bathrooms}</div>
              </div>
              <div className="detail-row">
                <div className="detail-label">Price Per Person:</div>
                <div className="detail-value">${selectedProperty.price_per_person}</div>
              </div>
              {selectedProperty.remodel_status && (
                <div className="detail-row">
                  <div className="detail-label">Remodel Status:</div>
                  <div className="detail-value">{selectedProperty.remodel_status}</div>
                </div>
              )}
              {selectedProperty.furnish_status && (
                <div className="detail-row">
                  <div className="detail-label">Furnish Status:</div>
                  <div className="detail-value">{selectedProperty.furnish_status}</div>
                </div>
              )}
              {selectedProperty.laundry_location && (
                <div className="detail-row">
                  <div className="detail-label">Laundry:</div>
                  <div className="detail-value">{selectedProperty.laundry_location}</div>
                </div>
              )}
              {selectedProperty.lease_duration && (
                <div className="detail-row">
                  <div className="detail-label">Lease Duration:</div>
                  <div className="detail-value">{selectedProperty.lease_duration} months</div>
                </div>
              )}
              {selectedProperty.distance_to_walc && (
                <div className="detail-row">
                  <div className="detail-label">Distance to WALC:</div>
                  <div className="detail-value">{selectedProperty.distance_to_walc} miles</div>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setSelectedProperty(null)}>Close</button>
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  setShowEditModal(true);
                }}
              >
                Edit Property
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Create Property Modal */}
      {showCreateModal && (
        <PropertyForm 
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            fetchProperties();
            setAlertMessage({ type: 'success', text: 'Property created successfully' });
          }}
        />
      )}
      
      {/* Edit Property Modal */}
      {showEditModal && selectedProperty && (
        <PropertyForm 
          property={selectedProperty}
          onClose={() => {
            setShowEditModal(false);
            setSelectedProperty(null);
          }}
          onSuccess={() => {
            setShowEditModal(false);
            setSelectedProperty(null);
            fetchProperties();
            setAlertMessage({ type: 'success', text: 'Property updated successfully' });
          }}
        />
      )}
    </div>
  );
};

const PropertyForm = ({ property, onClose, onSuccess }) => {
  const isEditing = !!property;
  
  const initialState = {
    property_name: '',
    address: '',
    num_bedrooms: '',
    num_bathrooms: '',
    price_per_person: '',
    remodel_status: 'Not Remodeled',
    furnish_status: 'Unfurnished',
    laundry_location: 'In Unit',
    lease_duration: '12',
    distance_to_walc: ''
  };
  
  const [formData, setFormData] = useState(property || initialState);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
    
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: ''
      });
    }
  };
  
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.property_name.trim()) {
      newErrors.property_name = 'Property name is required';
    }
    
    if (!formData.address.trim()) {
      newErrors.address = 'Address is required';
    }
    
    if (!formData.num_bedrooms || formData.num_bedrooms < 0) {
      newErrors.num_bedrooms = 'Valid number of bedrooms is required';
    }
    
    if (!formData.num_bathrooms || formData.num_bathrooms < 0) {
      newErrors.num_bathrooms = 'Valid number of bathrooms is required';
    }
    
    if (!formData.price_per_person || formData.price_per_person <= 0) {
      newErrors.price_per_person = 'Valid price is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSubmitting(true);
    
    try {
      const url = isEditing 
        ? `http://localhost:5000/properties/${property.property_id}`
        : 'http://localhost:5000/properties';
      
      const method = isEditing ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        onSuccess();
      } else {
        const errorData = await response.json();
        setErrors({ form: errorData.error || 'Failed to save property' });
      }
    } catch (error) {
      console.error('Error saving property:', error);
      setErrors({ form: 'Failed to save property' });
    } finally {
      setSubmitting(false);
    }
  };
  
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>{isEditing ? 'Edit Property' : 'Add New Property'}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit}>
          {errors.form && <div className="alert alert-danger">{errors.form}</div>}
          
          <div className="form-group">
            <label htmlFor="property_name">Property Name *</label>
            <input
              type="text"
              id="property_name"
              name="property_name"
              value={formData.property_name}
              onChange={handleChange}
              className={errors.property_name ? 'error' : ''}
            />
            {errors.property_name && <div className="error-text">{errors.property_name}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="address">Address *</label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              className={errors.address ? 'error' : ''}
            />
            {errors.address && <div className="error-text">{errors.address}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="num_bedrooms">Number of Bedrooms *</label>
            <input
              type="number"
              id="num_bedrooms"
              name="num_bedrooms"
              value={formData.num_bedrooms}
              onChange={handleChange}
              min="0"
              className={errors.num_bedrooms ? 'error' : ''}
            />
            {errors.num_bedrooms && <div className="error-text">{errors.num_bedrooms}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="num_bathrooms">Number of Bathrooms *</label>
            <input
              type="number"
              id="num_bathrooms"
              name="num_bathrooms"
              value={formData.num_bathrooms}
              onChange={handleChange}
              min="0"
              step="0.5"
              className={errors.num_bathrooms ? 'error' : ''}
            />
            {errors.num_bathrooms && <div className="error-text">{errors.num_bathrooms}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="price_per_person">Price Per Person ($) *</label>
            <input
              type="number"
              id="price_per_person"
              name="price_per_person"
              value={formData.price_per_person}
              onChange={handleChange}
              min="0"
              className={errors.price_per_person ? 'error' : ''}
            />
            {errors.price_per_person && <div className="error-text">{errors.price_per_person}</div>}
          </div>
          
          <div className="form-group">
            <label htmlFor="remodel_status">Remodel Status</label>
            <select
              id="remodel_status"
              name="remodel_status"
              value={formData.remodel_status}
              onChange={handleChange}
            >
              <option value="Not Remodeled">Not Remodeled</option>
              <option value="Partially Remodeled">Partially Remodeled</option>
              <option value="Fully Remodeled">Fully Remodeled</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="furnish_status">Furnish Status</label>
            <select
              id="furnish_status"
              name="furnish_status"
              value={formData.furnish_status}
              onChange={handleChange}
            >
              <option value="Unfurnished">Unfurnished</option>
              <option value="Partially Furnished">Partially Furnished</option>
              <option value="Fully Furnished">Fully Furnished</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="laundry_location">Laundry Location</label>
            <select
              id="laundry_location"
              name="laundry_location"
              value={formData.laundry_location}
              onChange={handleChange}
            >
              <option value="In Unit">In Unit</option>
              <option value="In Building">In Building</option>
              <option value="None">None</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="lease_duration">Lease Duration (months)</label>
            <input
              type="number"
              id="lease_duration"
              name="lease_duration"
              value={formData.lease_duration}
              onChange={handleChange}
              min="1"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="distance_to_walc">Distance to WALC (miles)</label>
            <input
              type="number"
              id="distance_to_walc"
              name="distance_to_walc"
              value={formData.distance_to_walc}
              onChange={handleChange}
              min="0"
              step="0.1"
            />
          </div>
          
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button 
              type="submit" 
              className="btn btn-primary" 
              disabled={submitting}
            >
              {submitting ? 'Saving...' : (isEditing ? 'Update Property' : 'Create Property')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PropertyList;