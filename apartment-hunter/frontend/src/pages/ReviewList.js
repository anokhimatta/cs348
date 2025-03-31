import React, { useEffect, useState } from "react";

function ReviewList() {
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/reviews")
      .then((res) => res.json())
      .then((data) => setReviews(data))
      .catch((error) => console.error("Error fetching reviews:", error));
  }, []);

  return (
    <div>
      <h1>Reviews</h1>
      {reviews.length === 0 ? (
        <p>No reviews available.</p>
      ) : (
        <ul>
          {reviews.map((review) => (
            <li key={review.id}>
              <h2>{review.renter_name}</h2>
              <p>Rating: {review.rating}/5</p>
              <p>{review.comment}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ReviewList;