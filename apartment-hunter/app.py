from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, create_engine, text
from sqlalchemy.ext.hybrid import hybrid_property
import os

app = Flask(__name__)
CORS(app)

# Configure SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "apartments3.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Models
class Renter(db.Model):
    __tablename__ = 'Renter'
    
    renter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    min_budget = db.Column(db.Float, nullable=False)
    max_budget = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    
    # Relationships
    applications = db.relationship('LeaseApplication', backref='renter', lazy=True)
    
    def to_dict(self):
        return {
            'renter_id': self.renter_id,
            'name': self.name,
            'email': self.email,
            'phone_number': self.phone_number,
            'min_budget': self.min_budget,
            'max_budget': self.max_budget,
            'credit_score': self.credit_score
        }


class Property(db.Model):
    __tablename__ = 'Property'
    
    property_id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    num_bedrooms = db.Column(db.Integer, nullable=False)
    num_bathrooms = db.Column(db.Float, nullable=False)
    price_per_person = db.Column(db.Float, nullable=False)
    
    # Relationships
    applications = db.relationship('LeaseApplication', backref='property', lazy=True)
    reviews = db.relationship('Review', backref='property', lazy=True)
    
    @hybrid_property
    def avg_rating(self):
        from sqlalchemy import func
        result = db.session.query(func.avg(Review.rating)).filter(Review.rev_property_id == self.property_id).scalar()
        return result or 0
    
    def to_dict(self):
        return {
            'property_id': self.property_id,
            'property_name': self.property_name,
            'address': self.address,
            'num_bedrooms': self.num_bedrooms,
            'num_bathrooms': self.num_bathrooms,
            'price_per_person': self.price_per_person,
            'avg_rating': self.avg_rating
        }


class LeaseApplication(db.Model):
    __tablename__ = 'LeaseApplications'
    
    application_id = db.Column(db.Integer, primary_key=True)
    app_renter_id = db.Column(db.Integer, db.ForeignKey('Renter.renter_id'), nullable=False)
    app_property_id = db.Column(db.Integer, db.ForeignKey('Property.property_id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'app_renter_id': self.app_renter_id,
            'app_property_id': self.app_property_id,
            'status': self.status,
            'renter_name': self.renter.name if self.renter else None,
            'property_name': self.property.property_name if self.property else None
        }


class Review(db.Model):
    __tablename__ = 'Reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    rev_property_id = db.Column(db.Integer, db.ForeignKey('Property.property_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'review_id': self.review_id,
            'rev_property_id': self.rev_property_id,
            'rating': self.rating,
            'comment': self.comment
        }


# Helper function
def is_within_budget(property_price, min_budget, max_budget):
    return min_budget <= property_price <= max_budget


# Renter CRUD
@app.route('/renters', methods=['GET'])
def get_renters():
    renters = Renter.query.all()
    return jsonify([renter.to_dict() for renter in renters])


@app.route('/renters/<int:renter_id>', methods=['GET'])
def get_renter(renter_id):
    renter = Renter.query.get(renter_id)
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    return jsonify(renter.to_dict())


@app.route('/renters', methods=['POST'])
def create_renter():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['renter_id', 'name', 'email', 'phone_number', 'min_budget', 'max_budget', 'credit_score']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        new_renter = Renter(
            renter_id=data['renter_id'],
            name=data['name'],
            email=data['email'],
            phone_number=data['phone_number'],
            min_budget=data['min_budget'],
            max_budget=data['max_budget'],
            credit_score=data['credit_score']
        )
        
        db.session.add(new_renter)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Renter created successfully"}), 201


@app.route('/renters/<int:renter_id>', methods=['PUT'])
def update_renter(renter_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    renter = Renter.query.get(renter_id)
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    update_fields = ['name', 'email', 'phone_number', 'min_budget', 'max_budget', 'credit_score']
    update_made = False
    
    for field in update_fields:
        if field in data:
            setattr(renter, field, data[field])
            update_made = True
    
    if not update_made:
        return jsonify({"error": "No fields to update"}), 400
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Renter updated successfully"})


@app.route('/renters/<int:renter_id>', methods=['DELETE'])
def delete_renter(renter_id):
    renter = Renter.query.get(renter_id)
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    try:
        db.session.delete(renter)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Cannot delete renter with related records"}), 400
    
    return jsonify({"success": True, "message": "Renter deleted successfully"})


# Property CRUD
@app.route('/properties', methods=['GET'])
def get_properties():
    properties = Property.query.all()
    return jsonify([prop.to_dict() for prop in properties])


@app.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    property = Property.query.get(property_id)
    
    if property is None:
        return jsonify({"error": "Property not found"}), 404
    
    return jsonify(property.to_dict())


@app.route('/properties', methods=['POST'])
def create_property():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = [
        'property_name', 'address', 'num_bedrooms', 'num_bathrooms', 'price_per_person'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        new_property = Property(
            property_name=data['property_name'],
            address=data['address'],
            num_bedrooms=data['num_bedrooms'],
            num_bathrooms=data['num_bathrooms'],
            price_per_person=data['price_per_person']
        )
        
        db.session.add(new_property)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Property created successfully", 
            "property_id": new_property.property_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/properties/<int:property_id>', methods=['PUT'])
def update_property(property_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    property = Property.query.get(property_id)
    
    if property is None:
        return jsonify({"error": "Property not found"}), 404
    
    update_fields = [
        'property_name', 'address', 'num_bedrooms', 'num_bathrooms', 'price_per_person'
    ]
    update_made = False
    
    for field in update_fields:
        if field in data:
            setattr(property, field, data[field])
            update_made = True
    
    if not update_made:
        return jsonify({"error": "No fields to update"}), 400
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Property updated successfully"})


@app.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    property = Property.query.get(property_id)
    
    if property is None:
        return jsonify({"error": "Property not found"}), 404
    
    try:
        db.session.delete(property)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Cannot delete property with related records"}), 400
    
    return jsonify({"success": True, "message": "Property deleted successfully"})


# LeaseApplications CRUD
@app.route('/applications', methods=['GET'])
def get_applications():
    applications = LeaseApplication.query.all()
    return jsonify([app.to_dict() for app in applications])


@app.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = LeaseApplication.query.get(application_id)
    
    if application is None:
        return jsonify({"error": "Application not found"}), 404
    
    return jsonify(application.to_dict())


@app.route('/applications', methods=['POST'])
def create_application():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['app_renter_id', 'app_property_id', 'status']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    renter = Renter.query.get(data['app_renter_id'])
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    property = Property.query.get(data['app_property_id'])
    if property is None:
        return jsonify({"error": "Property not found"}), 404
    
    # Check if property is within budget
    if not is_within_budget(property.price_per_person, renter.min_budget, renter.max_budget):
        return jsonify({"error": "Property price is outside renter's budget range"}), 400
    
    try:
        new_application = LeaseApplication(
            app_renter_id=data['app_renter_id'],
            app_property_id=data['app_property_id'],
            status=data['status']
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Application created successfully", 
            "application_id": new_application.application_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@app.route('/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    application = LeaseApplication.query.get(application_id)
    
    if application is None:
        return jsonify({"error": "Application not found"}), 404
    
    # Special case for status-only updates
    if 'status' in data and len(data) == 1:
        try:
            application.status = data['status']
            db.session.commit()
            return jsonify({"success": True, "message": "Application status updated successfully"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
    
    update_fields = ['app_renter_id', 'app_property_id', 'status']
    update_made = False
    
    for field in update_fields:
        if field in data:
            setattr(application, field, data[field])
            update_made = True
    
    if not update_made:
        return jsonify({"error": "No fields to update"}), 400
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Application updated successfully"})


@app.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    application = LeaseApplication.query.get(application_id)
    
    if application is None:
        return jsonify({"error": "Application not found"}), 404
    
    try:
        db.session.delete(application)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Application deleted successfully"})


# Budget endpoint
@app.route('/properties/budget/<float:min_price>/<float:max_price>', methods=['GET'])
def get_properties_by_budget(min_price, max_price):
    try:
        properties = Property.query.filter(
            Property.price_per_person.between(min_price, max_price)
        ).all()
        
        return jsonify([prop.to_dict() for prop in properties])
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Create the database tables if they don't exist yet
    with app.app_context():
        db.create_all()
    app.run(debug=True)