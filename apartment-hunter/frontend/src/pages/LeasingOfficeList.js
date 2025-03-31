import React, { useEffect, useState } from "react";

function LeasingOfficeList() {
  const [offices, setOffices] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/leasing-offices")
      .then((res) => res.json())
      .then((data) => setOffices(data))
      .catch((error) => console.error("Error fetching offices:", error));
  }, []);

  return (
    <div>
      <h1>Leasing Offices</h1>
      {offices.length === 0 ? (
        <p>No leasing offices available.</p>
      ) : (
        <ul>
          {offices.map((office) => (
            <li key={office.id}>
              <h2>{office.name}</h2>
              <p>Location: {office.location}</p>
              <p>Contact: {office.contact}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default LeasingOfficeList;