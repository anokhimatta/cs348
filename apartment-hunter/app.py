from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func, create_engine, text
import os

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "apartments3.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

# ORM Layer
class Renter(db.Model):
    __tablename__ = 'Renter'
    
    renter_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    min_budget = db.Column(db.Float, nullable=False)
    max_budget = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    
    # Relationships (ORM)
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
    
    # Relationships (ORM)
    applications = db.relationship('LeaseApplication', backref='property', lazy=True)
    
    def to_dict(self):
        return {
            'property_id': self.property_id,
            'property_name': self.property_name,
            'address': self.address,
            'num_bedrooms': self.num_bedrooms,
            'num_bathrooms': self.num_bathrooms,
            'price_per_person': self.price_per_person,
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


# Helper function
def is_within_budget(property_price, min_budget, max_budget):
    return min_budget <= property_price <= max_budget


# Renter CRUD
@app.route('/renters', methods=['GET'])
def get_renters():
    # Prepared Statement
    with engine.connect() as connection:
        query = text("SELECT * FROM Renter")
        result = connection.execute(query)
        renters = []
        for row in result:
            renter = {
                'renter_id': row[0],
                'name': row[1],
                'email': row[2],
                'phone_number': row[3],
                'min_budget': row[4],
                'max_budget': row[5],
                'credit_score': row[6]
            }
            renters.append(renter)
        return jsonify(renters)


@app.route('/renters/<int:renter_id>', methods=['GET'])
def get_renter(renter_id):
    # Prepared Statement
    with engine.connect() as connection:
        query = text("SELECT * FROM Renter WHERE renter_id = :renter_id")
        result = connection.execute(query, {"renter_id": renter_id}).fetchone()
        
        if result is None:
            return jsonify({"error": "Renter not found"}), 404
        
        renter = {
            'renter_id': result[0],
            'name': result[1],
            'email': result[2],
            'phone_number': result[3],
            'min_budget': result[4],
            'max_budget': result[5],
            'credit_score': result[6]
        }
        
        return jsonify(renter)


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
        # Using Prepared Statement
        with engine.connect() as connection:
            with connection.begin():
                query = text("""
                    INSERT INTO Renter (renter_id, name, email, phone_number, min_budget, max_budget, credit_score) 
                    VALUES (:renter_id, :name, :email, :phone_number, :min_budget, :max_budget, :credit_score)
                """)
                
                connection.execute(query, {
                    "renter_id": data['renter_id'],
                    "name": data['name'],
                    "email": data['email'],
                    "phone_number": data['phone_number'],
                    "min_budget": data['min_budget'],
                    "max_budget": data['max_budget'],
                    "credit_score": data['credit_score']
                })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Renter created successfully"}), 201


@app.route('/renters/<int:renter_id>', methods=['PUT'])
def update_renter(renter_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    # ORM
    renter = Renter.query.get(renter_id)
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    update_fields = ['name', 'email', 'phone_number', 'min_budget', 'max_budget', 'credit_score']
    update_data = {}
    update_made = False
    
    for field in update_fields:
        if field in data:
            update_data[field] = data[field]
            update_made = True
    
    if not update_made:
        return jsonify({"error": "No fields to update"}), 400
    
    try:
        # Prepared Statement
        with engine.connect() as connection:
            with connection.begin():
                set_clauses = []
                params = {"renter_id": renter_id}
                
                for field, value in update_data.items():
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
                
                query_str = f"UPDATE Renter SET {', '.join(set_clauses)} WHERE renter_id = :renter_id"
                query = text(query_str)
                
                connection.execute(query, params)
                
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Renter updated successfully"})



@app.route('/renters/<int:renter_id>', methods=['DELETE'])
def delete_renter(renter_id):
    # ORM
    renter = Renter.query.get(renter_id)
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    try:
        # Prepared Statement
        with engine.connect() as connection:
            with connection.begin():
                delete_apps_query = text("""
                    DELETE FROM LeaseApplications WHERE app_renter_id = :renter_id
                """)
                connection.execute(delete_apps_query, {"renter_id": renter_id})
                
                delete_renter_query = text("DELETE FROM Renter WHERE renter_id = :renter_id")
                connection.execute(delete_renter_query, {"renter_id": renter_id})
                
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({
        "success": True, 
        "message": "Renter and all associated lease applications deleted successfully"
    })


# Property CRUD
@app.route('/properties', methods=['GET'])
def get_properties():
    # ORM
    properties = Property.query.all()
    return jsonify([prop.to_dict() for prop in properties])


@app.route('/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    # Prepared Statement
    with engine.connect() as connection:
        query = text("SELECT * FROM Property WHERE property_id = :property_id")
        result = connection.execute(query, {"property_id": property_id}).fetchone()
        
        if result is None:
            return jsonify({"error": "Property not found"}), 404
        
        property = {
            'property_id': result[0],
            'property_name': result[1],
            'address': result[2],
            'num_bedrooms': result[3],
            'num_bathrooms': result[4],
            'price_per_person': result[5]
        }
        
        return jsonify(property)


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
        # ORM
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
    
    # Prepared Statement
    with engine.connect() as connection:
        check_query = text("SELECT COUNT(*) FROM Property WHERE property_id = :property_id")
        exists = connection.execute(check_query, {"property_id": property_id}).scalar() > 0
        
        if not exists:
            return jsonify({"error": "Property not found"}), 404
    
    update_fields = [
        'property_name', 'address', 'num_bedrooms', 'num_bathrooms', 'price_per_person'
    ]
    update_data = {}
    update_made = False
    
    for field in update_fields:
        if field in data:
            update_data[field] = data[field]
            update_made = True
    
    if not update_made:
        return jsonify({"error": "No fields to update"}), 400
    
    try:
        # Prepared Statement
        with engine.connect() as connection:
            with connection.begin():
                set_clauses = []
                params = {"property_id": property_id}
                
                for field, value in update_data.items():
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value
                
                query_str = f"UPDATE Property SET {', '.join(set_clauses)} WHERE property_id = :property_id"
                query = text(query_str)
                
                connection.execute(query, params)
                
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Property updated successfully"})


@app.route('/properties/<int:property_id>', methods=['DELETE'])
def delete_property(property_id):
    # ORM and prepared statement
    property = Property.query.get(property_id)
    
    if property is None:
        return jsonify({"error": "Property not found"}), 404
    
    try:
        # Prepared Statement
        with engine.connect() as connection:
            with connection.begin():
                check_query = text("""
                    SELECT COUNT(*) FROM LeaseApplications WHERE app_property_id = :property_id
                """)
                app_count = connection.execute(check_query, {"property_id": property_id}).scalar()
                
                if app_count > 0:
                    return jsonify({"error": "Cannot delete property with related records"}), 400
                
                delete_query = text("DELETE FROM Property WHERE property_id = :property_id")
                connection.execute(delete_query, {"property_id": property_id})
                
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"success": True, "message": "Property deleted successfully"})


# LeaseApplications CRUD
@app.route('/applications', methods=['GET'])
def get_applications():
    # ORM
    applications = db.session.query(LeaseApplication).all()
    return jsonify([app.to_dict() for app in applications])


@app.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    # Prepared Statement
    with engine.connect() as connection:
        query = text("""
            SELECT la.*, r.name as renter_name, p.property_name 
            FROM LeaseApplications la
            JOIN Renter r ON la.app_renter_id = r.renter_id
            JOIN Property p ON la.app_property_id = p.property_id
            WHERE la.application_id = :application_id
        """)
        
        result = connection.execute(query, {"application_id": application_id}).fetchone()
        
        if result is None:
            return jsonify({"error": "Application not found"}), 404
        
        application = {
            'application_id': result[0],
            'app_renter_id': result[1],
            'app_property_id': result[2],
            'status': result[3],
            'renter_name': result[4],
            'property_name': result[5]
        }
        
        return jsonify(application)


@app.route('/applications', methods=['POST'])
def create_application():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['app_renter_id', 'app_property_id', 'status']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        with engine.connect() as validation_conn:
            renter_query = text("SELECT min_budget, max_budget FROM Renter WHERE renter_id = :renter_id")
            renter_result = validation_conn.execute(renter_query, {"renter_id": data['app_renter_id']}).fetchone()
            
            if renter_result is None:
                return jsonify({"error": "Renter not found"}), 404
            
            min_budget, max_budget = renter_result
            
            property_query = text("SELECT price_per_person FROM Property WHERE property_id = :property_id")
            property_result = validation_conn.execute(property_query, {"property_id": data['app_property_id']}).fetchone()
            
            if property_result is None:
                return jsonify({"error": "Property not found"}), 404
            
            price_per_person = property_result[0]
            
            if not is_within_budget(price_per_person, min_budget, max_budget):
                return jsonify({"error": "Property price is outside renter's budget range"}), 400
        
        with engine.connect() as transaction_conn:
            # Prepared statement
            with transaction_conn.begin():
                insert_query = text("""
                    INSERT INTO LeaseApplications (app_renter_id, app_property_id, status) 
                    VALUES (:app_renter_id, :app_property_id, :status)
                """)
                
                transaction_conn.execute(insert_query, {
                    "app_renter_id": data['app_renter_id'],
                    "app_property_id": data['app_property_id'],
                    "status": data['status']
                })
                
                last_id_query = text("SELECT last_insert_rowid()")
                application_id = transaction_conn.execute(last_id_query).scalar()
                
        return jsonify({
            "success": True, 
            "message": "Application created successfully", 
            "application_id": application_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/applications/<int:application_id>', methods=['PUT'])
def update_application(application_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    # Prepared statement
    with engine.connect() as connection:
        check_query = text("SELECT COUNT(*) FROM LeaseApplications WHERE application_id = :application_id")
        exists = connection.execute(check_query, {"application_id": application_id}).scalar() > 0
        
        if not exists:
            return jsonify({"error": "Application not found"}), 404
    
    if 'status' in data and len(data) == 1:
        try:
            # Prepared Statement
            with engine.connect() as connection:
                with connection.begin():
                    update_query = text("""
                        UPDATE LeaseApplications SET status = :status 
                        WHERE application_id = :application_id
                    """)
                    
                    connection.execute(update_query, {
                        "status": data['status'],
                        "application_id": application_id
                    })
                    
                    return jsonify({"success": True, "message": "Application status updated successfully"})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    
    # ORM
    update_fields = ['app_renter_id', 'app_property_id', 'status']
    application = LeaseApplication.query.get(application_id) 
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
    try:
        with engine.connect() as connection:
            check_query = text("SELECT COUNT(*) FROM LeaseApplications WHERE application_id = :application_id")
            exists = connection.execute(check_query, {"application_id": application_id}).scalar() > 0
            
            if not exists:
                return jsonify({"error": "Application not found"}), 404
        
        with engine.connect() as connection:
            with connection.begin():
                delete_query = text("DELETE FROM LeaseApplications WHERE application_id = :application_id")
                connection.execute(delete_query, {"application_id": application_id})
            
        return jsonify({"success": True, "message": "Application deleted successfully"})
            
    except Exception as e:
        print(f"Error deleting application {application_id}: {str(e)}")
        return jsonify({"error": f"Failed to delete application: {str(e)}"}), 400


# prepared statement
@app.route('/properties/budget/<float:min_price>/<float:max_price>', methods=['GET'])
def get_properties_by_budget(min_price, max_price):
    try:
        # Prepared Statement
        with engine.connect() as connection:
            query = text("""
                SELECT * FROM Property 
                WHERE price_per_person BETWEEN :min_price AND :max_price
            """)
            
            result = connection.execute(query, {
                "min_price": min_price,
                "max_price": max_price
            })
            
            properties = []
            for row in result:
                property = {
                    'property_id': row[0],
                    'property_name': row[1],
                    'address': row[2],
                    'num_bedrooms': row[3],
                    'num_bathrooms': row[4],
                    'price_per_person': row[5]
                }
                properties.append(property)
            
            return jsonify(properties)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)