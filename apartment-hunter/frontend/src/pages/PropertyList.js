import React from "react";

function PropertyList({ properties }) {
  return (
    <div>
      {properties.length === 0 ? (
        <p>No properties available.</p>
      ) : (
        <ul>
          {properties.map((property) => (
            <li key={property.id}>
              <h2>{property.name}</h2>
              <p>Location: {property.location}</p>
              <p>Price: ${property.price}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default PropertyList;