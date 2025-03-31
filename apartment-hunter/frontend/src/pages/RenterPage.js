import React, { useEffect, useState } from "react";
import RenterList from "../components/RenterList";

function RenterPage() {
  const [renters, setRenters] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/renters")
      .then((res) => res.json())
      .then((data) => setRenters(data))
      .catch((error) => console.error("Error fetching renters:", error));
  }, []);

  return (
    <div>
      <h1>Renters</h1>
      <RenterList renters={renters} />
    </div>
  );
}

export default RenterPage;