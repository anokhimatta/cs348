import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'apartments3.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (dict(rv[0]) if rv else None) if one else [dict(row) for row in rv]

def execute_db(query, args=()):
    conn = get_db()
    conn.execute(query, args)
    conn.commit()

def initialize_stored_procedures():
    conn = get_db()
    
    conn.execute('''
    CREATE TEMP FUNCTION IF NOT EXISTS get_property_avg_rating(prop_id INTEGER) 
    RETURNS REAL 
    BEGIN
        RETURN (SELECT AVG(rating) FROM Reviews WHERE rev_property_id = prop_id);
    END;
    ''')
    
    conn.execute('''
    CREATE TEMP FUNCTION IF NOT EXISTS is_within_budget(prop_price REAL, min_budget REAL, max_budget REAL) 
    RETURNS INTEGER
    BEGIN
        RETURN CASE WHEN prop_price >= min_budget AND prop_price <= max_budget THEN 1 ELSE 0 END;
    END;
    ''')
    
    conn.commit()

@app.before_first_request
def before_first_request():
    initialize_stored_procedures()

# Renter API Routes
@app.route('/api/renters', methods=['GET'])
def get_renters():
    renters = query_db('SELECT * FROM Renter')
    return jsonify(renters)

@app.route('/api/renters/<renter_id>', methods=['GET'])
def get_renter(renter_id):
    renter = query_db('SELECT * FROM Renter WHERE renter_id = ?', [renter_id], one=True)
    if renter:
        return jsonify(renter)
    return jsonify({"error": "Renter not found"}), 404

@app.route('/api/renters', methods=['POST'])
def create_renter():
    data = request.get_json()
    try:
        execute_db('''
            INSERT INTO Renter (renter_id, name, email, phone_number, min_budget, max_budget, credit_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [
            data['renter_id'], 
            data['name'], 
            data['email'], 
            data['phone_number'], 
            data['min_budget'], 
            data['max_budget'],
            data['credit_score']
        ])
        return jsonify({"message": "Renter created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/renters/<renter_id>', methods=['PUT'])
def update_renter(renter_id):
    data = request.get_json()
    try:
        execute_db('''
            UPDATE Renter
            SET name = ?, email = ?, phone_number = ?, min_budget = ?, max_budget = ?, credit_score = ?
            WHERE renter_id = ?
        ''', [
            data['name'], 
            data['email'], 
            data['phone_number'], 
            data['min_budget'], 
            data['max_budget'],
            data['credit_score'],
            renter_id
        ])
        return jsonify({"message": "Renter updated successfully"})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/renters/<renter_id>', methods=['DELETE'])
def delete_renter(renter_id):
    execute_db('DELETE FROM Renter WHERE renter_id = ?', [renter_id])
    return jsonify({"message": "Renter deleted successfully"})

# Property API Routes
@app.route('/api/properties', methods=['GET'])
def get_properties():
    properties = query_db('''
        SELECT p.*, get_property_avg_rating(p.property_id) as avg_rating 
        FROM Property p
    ''')
    return jsonify(properties)

@app.route('/api/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    property = query_db('''
        SELECT p.*, get_property_avg_rating(p.property_id) as avg_rating 
        FROM Property p
        WHERE p.property_id = ?
    ''', [property_id], one=True)
    if property:
        return jsonify(property)
    return jsonify({"error": "Property not found"}), 404

@app.route('/api/properties', methods=['POST'])
def create_property():
    data = request.get_json()
    try:
        execute_db('''
            INSERT INTO Property (office_id, property_name, address, remodel_status, furnish_status, 
                                  num_bedrooms, num_bathrooms, laundry_location, lease_duration, 
                                  price_per_person, distance_to_walc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', [
            data.get('office_id'),
            data['property_name'], 
            data['address'],
            data['remodel_status'],
            data['furnish_status'],
            data['num_bedrooms'],
            data['num_bathrooms'],
            data['laundry_location'],
            data['lease_duration'],
            data['price_per_person'],
            data['distance_to_walc']
        ])
        return jsonify({"message": "Property created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    data = request.get_json()
    try:
        execute_db('''
            UPDATE Property
            SET office_id = ?, property_name = ?, address = ?, remodel_status = ?, furnish_status = ?,
                num_bedrooms = ?, num_bathrooms = ?, laundry_location = ?, lease_duration = ?,
                price_per_person = ?, distance_to_walc = ?
            WHERE property_id = ?
        ''', [
            data.get('office_id'),
            data['property_name'], 
            data['address'],
            data['remodel_status'],
            data['furnish_status'],
            data['num_bedrooms'],
            data['num_bathrooms'],
            data['laundry_location'],
            data['lease_duration'],
            data['price_per_person'],
            data['distance_to_walc'],
            property_id
        ])
        return jsonify({"message": "Property updated successfully"})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/properties/<property_id>', methods=['DELETE'])
def delete_property(property_id):
    execute_db('DELETE FROM Property WHERE property_id = ?', [property_id])
    return jsonify({"message": "Property deleted successfully"})

# Leasing Office API Routes
@app.route('/api/offices', methods=['GET'])
def get_offices():
    offices = query_db('SELECT * FROM LeasingOffice')
    return jsonify(offices)

@app.route('/api/offices/<office_id>', methods=['GET'])
def get_office(office_id):
    office = query_db('SELECT * FROM LeasingOffice WHERE office_id = ?', [office_id], one=True)
    if office:
        return jsonify(office)
    return jsonify({"error": "Leasing office not found"}), 404

@app.route('/api/offices', methods=['POST'])
def create_office():
    data = request.get_json()
    try:
        execute_db('''
            INSERT INTO LeasingOffice (name, address, email, phone_number, open_hour, close_hour)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', [
            data['name'], 
            data['address'], 
            data['email'], 
            data['phone_number'], 
            data['open_hour'], 
            data['close_hour']
        ])
        return jsonify({"message": "Leasing office created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/offices/<office_id>', methods=['PUT'])
def update_office(office_id):
    data = request.get_json()
    try:
        execute_db('''
            UPDATE LeasingOffice
            SET name = ?, address = ?, email = ?, phone_number = ?, open_hour = ?, close_hour = ?
            WHERE office_id = ?
        ''', [
            data['name'], 
            data['address'], 
            data['email'], 
            data['phone_number'], 
            data['open_hour'], 
            data['close_hour'],
            office_id
        ])
        return jsonify({"message": "Leasing office updated successfully"})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/offices/<office_id>', methods=['DELETE'])
def delete_office(office_id):
    execute_db('DELETE FROM LeasingOffice WHERE office_id = ?', [office_id])
    return jsonify({"message": "Leasing office deleted successfully"})

# Lease Applications API Routes
@app.route('/api/applications', methods=['GET'])
def get_applications():
    applications = query_db('''
        SELECT la.*, r.name as renter_name, p.property_name
        FROM LeaseApplications la
        JOIN Renter r ON la.app_renter_id = r.renter_id
        JOIN Property p ON la.app_property_id = p.property_id
    ''')
    return jsonify(applications)

@app.route('/api/applications/<application_id>', methods=['GET'])
def get_application(application_id):
    application = query_db('''
        SELECT la.*, r.name as renter_name, p.property_name
        FROM LeaseApplications la
        JOIN Renter r ON la.app_renter_id = r.renter_id
        JOIN Property p ON la.app_property_id = p.property_id
        WHERE la.application_id = ?
    ''', [application_id], one=True)
    if application:
        return jsonify(application)
    return jsonify({"error": "Application not found"}), 404

@app.route('/api/applications', methods=['POST'])
def create_application():
    data = request.get_json()
    try:
        execute_db('''
            INSERT INTO LeaseApplications (app_renter_id, app_property_id, status)
            VALUES (?, ?, ?)
        ''', [
            data['app_renter_id'], 
            data['app_property_id'], 
            data['status']
        ])
        return jsonify({"message": "Lease application created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/applications/<application_id>', methods=['PUT'])
def update_application(application_id):
    data = request.get_json()
    try:
        execute_db('''
            UPDATE LeaseApplications
            SET app_renter_id = ?, app_property_id = ?, status = ?
            WHERE application_id = ?
        ''', [
            data['app_renter_id'], 
            data['app_property_id'], 
            data['status'],
            application_id
        ])
        return jsonify({"message": "Lease application updated successfully"})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/applications/<application_id>', methods=['DELETE'])
def delete_application(application_id):
    execute_db('DELETE FROM LeaseApplications WHERE application_id = ?', [application_id])
    return jsonify({"message": "Lease application deleted successfully"})

# Reviews API Routes
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    reviews = query_db('''
        SELECT r.*, rn.name as renter_name, 
               CASE 
                   WHEN r.rev_property_id IS NOT NULL THEN p.property_name 
                   ELSE NULL 
               END as property_name,
               CASE 
                   WHEN r.rev_office_id IS NOT NULL THEN o.name 
                   ELSE NULL 
               END as office_name
        FROM Reviews r
        LEFT JOIN Renter rn ON r.rev_renter_id = rn.renter_id
        LEFT JOIN Property p ON r.rev_property_id = p.property_id
        LEFT JOIN LeasingOffice o ON r.rev_office_id = o.office_id
    ''')
    return jsonify(reviews)

@app.route('/api/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    review = query_db('''
        SELECT r.*, rn.name as renter_name, 
               CASE 
                   WHEN r.rev_property_id IS NOT NULL THEN p.property_name 
                   ELSE NULL 
               END as property_name,
               CASE 
                   WHEN r.rev_office_id IS NOT NULL THEN o.name 
                   ELSE NULL 
               END as office_name
        FROM Reviews r
        LEFT JOIN Renter rn ON r.rev_renter_id = rn.renter_id
        LEFT JOIN Property p ON r.rev_property_id = p.property_id
        LEFT JOIN LeasingOffice o ON r.rev_office_id = o.office_id
        WHERE r.review_id = ?
    ''', [review_id], one=True)
    if review:
        return jsonify(review)
    return jsonify({"error": "Review not found"}), 404

@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.get_json()
    try:
        execute_db('''
            INSERT INTO Reviews (rev_renter_id, rev_property_id, rev_office_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            data.get('rev_renter_id'), 
            data.get('rev_property_id'), 
            data.get('rev_office_id'),
            data['rating'],
            data.get('comment')
        ])
        return jsonify({"message": "Review created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    data = request.get_json()
    try:
        execute_db('''
            UPDATE Reviews
            SET rev_renter_id = ?, rev_property_id = ?, rev_office_id = ?, rating = ?, comment = ?
            WHERE review_id = ?
        ''', [
            data.get('rev_renter_id'), 
            data.get('rev_property_id'), 
            data.get('rev_office_id'),
            data['rating'],
            data.get('comment'),
            review_id
        ])
        return jsonify({"message": "Review updated successfully"})
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    execute_db('DELETE FROM Reviews WHERE review_id = ?', [review_id])
    return jsonify({"message": "Review deleted successfully"})

@app.route('/api/search/properties', methods=['GET'])
def search_properties():
    min_budget = request.args.get('min_budget', type=float)
    max_budget = request.args.get('max_budget', type=float)
    min_bedrooms = request.args.get('min_bedrooms', type=int)
    max_distance = request.args.get('max_distance', type=float)
    furnish_status = request.args.get('furnish_status')
    
    query = 'SELECT p.*, get_property_avg_rating(p.property_id) as avg_rating FROM Property p WHERE 1=1'
    params = []
    
    if min_budget is not None and max_budget is not None:
        query += ' AND is_within_budget(p.price_per_person, ?, ?) = 1'
        params.extend([min_budget, max_budget])
    
    if min_bedrooms is not None:
        query += ' AND p.num_bedrooms >= ?'
        params.append(min_bedrooms)
    
    if max_distance is not None:
        query += ' AND p.distance_to_walc <= ?'
        params.append(max_distance)
    
    if furnish_status:
        query += ' AND p.furnish_status = ?'
        params.append(furnish_status)
    
    properties = query_db(query, params)
    return jsonify(properties)

@app.route('/api/search/recommended', methods=['GET'])
def get_recommended_properties():
    renter_id = request.args.get('renter_id')
    if not renter_id:
        return jsonify({"error": "Renter ID is required"}), 400
    
    recommended = query_db('''
        SELECT p.*, get_property_avg_rating(p.property_id) as avg_rating
        FROM Property p, Renter r
        WHERE r.renter_id = ?
        AND is_within_budget(p.price_per_person, r.min_budget, r.max_budget) = 1
        ORDER BY avg_rating DESC, p.distance_to_walc ASC
        LIMIT 5
    ''', [renter_id])
    
    return jsonify(recommended)

if __name__ == '__main__':
    app.run(debug=True)