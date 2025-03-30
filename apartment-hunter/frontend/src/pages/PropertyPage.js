import React, { useEffect, useState } from "react";
import PropertyList from "../components/PropertyList";

function PropertyPage() {
  const [properties, setProperties] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/properties")
      .then((res) => res.json())
      .then((data) => setProperties(data))
      .catch((error) => console.error("Error fetching properties:", error));
  }, []);

  return (
    <div>
      <h1>Properties</h1>
      <PropertyList properties={properties} />
    </div>
  );
}

export default PropertyPage;