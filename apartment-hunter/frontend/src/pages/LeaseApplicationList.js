import React, { useEffect, useState } from "react";

function LeaseApplicationList() {
  const [applications, setApplications] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/lease-applications")
      .then((res) => res.json())
      .then((data) => setApplications(data))
      .catch((error) => console.error("Error fetching applications:", error));
  }, []);

  return (
    <div>
      <h1>Lease Applications</h1>
      {applications.length === 0 ? (
        <p>No applications found.</p>
      ) : (
        <ul>
          {applications.map((application) => (
            <li key={application.id}>
              <h2>Applicant: {application.renter_name}</h2>
              <p>Property: {application.property_name}</p>
              <p>Status: {application.status}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default LeaseApplicationList;