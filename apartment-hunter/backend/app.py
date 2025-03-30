from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask import CORS
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'apartments.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

Base = automap_base()
Base.prepare(db.engine, reflect=True)

Property = Base.classes.Property
Renter = Base.classes.Renter
LeasingOffice = Base.classes['Leasing Office']
LeaseApplication = Base.classes['Lease Application']
Review = Base.classes.Reviews

@app.route('/api/properties', methods=['GET'])
def get_properties():
    properties = db.session.query(Property).all()
    result = []
    
    for property in properties:
        property_data = {c.name: getattr(property, c.name) for c in property.__table__.columns}
        result.append(property_data)
    
    return jsonify(result)

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    property = db.session.query(Property).filter_by(id=id).first_or_404()
    property_data = {c.name: getattr(property, c.name) for c in property.__table__.columns}
    return jsonify(property_data)

@app.route('/api/properties', methods=['POST'])
def create_property():
    data = request.get_json()
    new_property = Property(**data)
    db.session.add(new_property)
    db.session.commit()
    return jsonify({"message": "Property added", "id": new_property.id}), 201

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    property = db.session.query(Property).filter_by(id=id).first_or_404()
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(property, key):
            setattr(property, key, value)
    
    db.session.commit()
    return jsonify({"message": "Property updated"})

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    property = db.session.query(Property).filter_by(id=id).first_or_404()
    db.session.delete(property)
    db.session.commit()
    return jsonify({"message": "Property deleted"})

@app.route('/api/renters', methods=['GET'])
def get_renters():
    renters = db.session.query(Renter).all()
    result = []
    
    for renter in renters:
        renter_data = {c.name: getattr(renter, c.name) for c in renter.__table__.columns}
        result.append(renter_data)
    
    return jsonify(result)

@app.route('/api/renters/<int:id>', methods=['GET'])
def get_renter(id):
    renter = db.session.query(Renter).filter_by(id=id).first_or_404()
    renter_data = {c.name: getattr(renter, c.name) for c in renter.__table__.columns}
    return jsonify(renter_data)

@app.route('/api/renters', methods=['POST'])
def create_renter():
    data = request.get_json()
    new_renter = Renter(**data)
    db.session.add(new_renter)
    db.session.commit()
    return jsonify({"message": "Renter added", "id": new_renter.id}), 201

@app.route('/api/renters/<int:id>', methods=['PUT'])
def update_renter(id):
    renter = db.session.query(Renter).filter_by(id=id).first_or_404()
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(renter, key):
            setattr(renter, key, value)
    
    db.session.commit()
    return jsonify({"message": "Renter updated"})

@app.route('/api/renters/<int:id>', methods=['DELETE'])
def delete_renter(id):
    renter = db.session.query(Renter).filter_by(id=id).first_or_404()
    db.session.delete(renter)
    db.session.commit()
    return jsonify({"message": "Renter deleted"})

if __name__ == '__main__':
    app.run(debug=True)