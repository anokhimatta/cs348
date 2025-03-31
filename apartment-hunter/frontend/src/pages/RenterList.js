import React from "react";

function RenterList({ renters }) {
  return (
    <div>
      {renters.length === 0 ? (
        <p>No renters found.</p>
      ) : (
        <ul>
          {renters.map((renter) => (
            <li key={renter.id}>
              <h2>{renter.name}</h2>
              <p>Email: {renter.email}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default RenterList;