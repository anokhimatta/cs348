// apiService.js

const API_BASE_URL = 'http://localhost:5000';

// Renter API calls
export const getAllRenters = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/renters`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch renters');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching renters:', error);
    throw error;
  }
};

export const getRenter = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/renters/${id}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch renter details');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching renter ${id}:`, error);
    throw error;
  }
};

export const createRenter = async (renterData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/renters`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(renterData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create renter');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating renter:', error);
    throw error;
  }
};

export const updateRenter = async (id, renterData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/renters/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(renterData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update renter');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error updating renter ${id}:`, error);
    throw error;
  }
};

export const deleteRenter = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/renters/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to delete renter');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error deleting renter ${id}:`, error);
    throw error;
  }
};

// Applications related to renters
export const getRenterApplications = async (renterId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/applications`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch applications');
    }
    const allApplications = await response.json();
    // Filter applications for this specific renter
    return allApplications.filter(app => app.app_renter_id.toString() === renterId.toString());
  } catch (error) {
    console.error(`Error fetching applications for renter ${renterId}:`, error);
    throw error;
  }
};

// Property API calls
export const getAllProperties = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/properties`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch properties');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching properties:', error);
    throw error;
  }
};

export const getPropertiesWithinBudget = async (minPrice, maxPrice) => {
  try {
    const response = await fetch(`${API_BASE_URL}/properties/budget/${minPrice}/${maxPrice}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to fetch properties within budget');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching properties within budget range ${minPrice}-${maxPrice}:`, error);
    throw error;
  }
};

// Lease Application API calls
export const createApplication = async (applicationData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/applications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(applicationData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to create application');
    }
    return await response.json();
  } catch (error) {
    console.error('Error creating application:', error);
    throw error;
  }
};

export const updateApplicationStatus = async (id, status) => {
  try {
    const response = await fetch(`${API_BASE_URL}/applications/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to update application status');
    }
    return await response.json();
  } catch (error) {
    console.error(`Error updating application ${id} status:`, error);
    throw error;
  }
};