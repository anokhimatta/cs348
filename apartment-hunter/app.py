from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_PATH = 'apartments3.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def calculate_property_avg_rating(property_id):
    conn = get_db_connection()
    result = conn.execute('SELECT AVG(rating) FROM Reviews WHERE rev_property_id = ?', (property_id,)).fetchone()[0]
    conn.close()
    return result or 0

def check_within_budget(property_price, min_budget, max_budget):
    return 1 if min_budget <= property_price <= max_budget else 0

def init_db():
    conn = get_db_connection()
    
    conn.create_function("get_property_avg_rating", 1, calculate_property_avg_rating)
    conn.create_function("is_within_budget", 3, check_within_budget)
    
    conn.close()

init_db()

# CRUD Operations for Renter
@app.route('/renters', methods=['GET'])
def get_renters():
    conn = get_db_connection()
    renters = conn.execute('SELECT * FROM Renter').fetchall()
    conn.close()
    
    return jsonify([dict(renter) for renter in renters])

@app.route('/renters/<renter_id>', methods=['GET'])
def get_renter(renter_id):
    conn = get_db_connection()
    renter = conn.execute('SELECT * FROM Renter WHERE renter_id = ?', (renter_id,)).fetchone()
    conn.close()
    
    if renter is None:
        return jsonify({"error": "Renter not found"}), 404
    
    return jsonify(dict(renter))

@app.route('/renters', methods=['POST'])
def create_renter():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['renter_id', 'name', 'email', 'phone_number', 'min_budget', 'max_budget', 'credit_score']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO Renter (renter_id, name, email, phone_number, min_budget, max_budget, credit_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['renter_id'], 
            data['name'], 
            data['email'], 
            data['phone_number'], 
            data['min_budget'], 
            data['max_budget'], 
            data['credit_score']
        ))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Renter created successfully"}), 201

@app.route('/renters/<renter_id>', methods=['PUT'])
def update_renter(renter_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    conn = get_db_connection()
    renter = conn.execute('SELECT * FROM Renter WHERE renter_id = ?', (renter_id,)).fetchone()
    
    if renter is None:
        conn.close()
        return jsonify({"error": "Renter not found"}), 404
    
    update_fields = []
    values = []
    
    for field in ['name', 'email', 'phone_number', 'min_budget', 'max_budget', 'credit_score']:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400
    
    sql = f"UPDATE Renter SET {', '.join(update_fields)} WHERE renter_id = ?"
    values.append(renter_id)
    
    try:
        conn.execute(sql, values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Renter updated successfully"})

@app.route('/renters/<renter_id>', methods=['DELETE'])
def delete_renter(renter_id):
    conn = get_db_connection()
    renter = conn.execute('SELECT * FROM Renter WHERE renter_id = ?', (renter_id,)).fetchone()
    
    if renter is None:
        conn.close()
        return jsonify({"error": "Renter not found"}), 404
    
    try:
        conn.execute('DELETE FROM Renter WHERE renter_id = ?', (renter_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": "Cannot delete renter with related records"}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Renter deleted successfully"})

@app.route('/properties', methods=['GET'])
def get_properties():
    conn = get_db_connection()
    properties = conn.execute('SELECT * FROM Property').fetchall()
    conn.close()
    
    return jsonify([dict(property) for property in properties])

@app.route('/properties/<property_id>', methods=['GET'])
def get_property(property_id):
    conn = get_db_connection()
    property = conn.execute('SELECT * FROM Property WHERE property_id = ?', (property_id,)).fetchone()
    
    if property is None:
        conn.close()
        return jsonify({"error": "Property not found"}), 404
    
    avg_rating = conn.execute('SELECT get_property_avg_rating(?)', (property_id,)).fetchone()[0]
    
    property_dict = dict(property)
    property_dict['avg_rating'] = avg_rating
    
    conn.close()
    return jsonify(property_dict)

@app.route('/properties', methods=['POST'])
def create_property():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = [
        'property_name', 'address', 'remodel_status', 'furnish_status', 
        'num_bedrooms', 'num_bathrooms', 'laundry_location', 
        'lease_duration', 'price_per_person', 'distance_to_walc'
    ]
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO Property (
                office_id, property_name, address, remodel_status, furnish_status,
                num_bedrooms, num_bathrooms, laundry_location, lease_duration,
                price_per_person, distance_to_walc
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
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
        ))
        conn.commit()
        last_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Property created successfully", "property_id": last_id}), 201

@app.route('/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    conn = get_db_connection()
    property = conn.execute('SELECT * FROM Property WHERE property_id = ?', (property_id,)).fetchone()
    
    if property is None:
        conn.close()
        return jsonify({"error": "Property not found"}), 404
    
    update_fields = []
    values = []
    
    fields = [
        'office_id', 'property_name', 'address', 'remodel_status', 'furnish_status',
        'num_bedrooms', 'num_bathrooms', 'laundry_location', 'lease_duration',
        'price_per_person', 'distance_to_walc'
    ]
    
    for field in fields:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400
    
    sql = f"UPDATE Property SET {', '.join(update_fields)} WHERE property_id = ?"
    values.append(property_id)
    
    try:
        conn.execute(sql, values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Property updated successfully"})

@app.route('/properties/<property_id>', methods=['DELETE'])
def delete_property(property_id):
    conn = get_db_connection()
    property = conn.execute('SELECT * FROM Property WHERE property_id = ?', (property_id,)).fetchone()
    
    if property is None:
        conn.close()
        return jsonify({"error": "Property not found"}), 404
    
    try:
        conn.execute('DELETE FROM Property WHERE property_id = ?', (property_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": "Cannot delete property with related records"}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Property deleted successfully"})

# CRUD Operations for LeasingOffice
@app.route('/offices', methods=['GET'])
def get_offices():
    conn = get_db_connection()
    offices = conn.execute('SELECT * FROM LeasingOffice').fetchall()
    conn.close()
    
    return jsonify([dict(office) for office in offices])

@app.route('/offices/<office_id>', methods=['GET'])
def get_office(office_id):
    conn = get_db_connection()
    office = conn.execute('SELECT * FROM LeasingOffice WHERE office_id = ?', (office_id,)).fetchone()
    
    if office is None:
        conn.close()
        return jsonify({"error": "Leasing office not found"}), 404
    
    properties = conn.execute('SELECT * FROM Property WHERE office_id = ?', (office_id,)).fetchall()
    
    office_dict = dict(office)
    office_dict['properties'] = [dict(prop) for prop in properties]
    
    conn.close()
    return jsonify(office_dict)

@app.route('/offices', methods=['POST'])
def create_office():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['name', 'address', 'email', 'phone_number', 'open_hour', 'close_hour']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO LeasingOffice (name, address, email, phone_number, open_hour, close_hour)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], 
            data['address'], 
            data['email'], 
            data['phone_number'], 
            data['open_hour'], 
            data['close_hour']
        ))
        conn.commit()
        last_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Leasing office created successfully", "office_id": last_id}), 201

@app.route('/offices/<office_id>', methods=['PUT'])
def update_office(office_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    conn = get_db_connection()
    office = conn.execute('SELECT * FROM LeasingOffice WHERE office_id = ?', (office_id,)).fetchone()
    
    if office is None:
        conn.close()
        return jsonify({"error": "Leasing office not found"}), 404
    
    update_fields = []
    values = []
    
    for field in ['name', 'address', 'email', 'phone_number', 'open_hour', 'close_hour']:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400
    
    sql = f"UPDATE LeasingOffice SET {', '.join(update_fields)} WHERE office_id = ?"
    values.append(office_id)
    
    try:
        conn.execute(sql, values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Leasing office updated successfully"})

@app.route('/offices/<office_id>', methods=['DELETE'])
def delete_office(office_id):
    conn = get_db_connection()
    office = conn.execute('SELECT * FROM LeasingOffice WHERE office_id = ?', (office_id,)).fetchone()
    
    if office is None:
        conn.close()
        return jsonify({"error": "Leasing office not found"}), 404
    
    try:
        conn.execute('DELETE FROM LeasingOffice WHERE office_id = ?', (office_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": "Cannot delete leasing office with related records"}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Leasing office deleted successfully"})

# CRUD Operations for LeaseApplications
@app.route('/applications', methods=['GET'])
def get_applications():
    conn = get_db_connection()
    applications = conn.execute('''
        SELECT a.*, r.name as renter_name, p.property_name 
        FROM LeaseApplications a
        JOIN Renter r ON a.app_renter_id = r.renter_id
        JOIN Property p ON a.app_property_id = p.property_id
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(app) for app in applications])

@app.route('/applications/<application_id>', methods=['GET'])
def get_application(application_id):
    conn = get_db_connection()
    application = conn.execute('''
        SELECT a.*, r.name as renter_name, p.property_name 
        FROM LeaseApplications a
        JOIN Renter r ON a.app_renter_id = r.renter_id
        JOIN Property p ON a.app_property_id = p.property_id
        WHERE a.application_id = ?
    ''', (application_id,)).fetchone()
    
    if application is None:
        conn.close()
        return jsonify({"error": "Application not found"}), 404
    
    conn.close()
    return jsonify(dict(application))

@app.route('/applications', methods=['POST'])
def create_application():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['app_renter_id', 'app_property_id', 'status']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    conn = get_db_connection()
    
    renter = conn.execute('SELECT * FROM Renter WHERE renter_id = ?', (data['app_renter_id'],)).fetchone()
    if renter is None:
        conn.close()
        return jsonify({"error": "Renter not found"}), 404
    
    property = conn.execute('SELECT * FROM Property WHERE property_id = ?', (data['app_property_id'],)).fetchone()
    if property is None:
        conn.close()
        return jsonify({"error": "Property not found"}), 404
    
    within_budget = conn.execute(
        'SELECT is_within_budget(?, ?, ?)', 
        (property['price_per_person'], renter['min_budget'], renter['max_budget'])
    ).fetchone()[0]
    
    if not within_budget:
        conn.close()
        return jsonify({"error": "Property price is outside renter's budget range"}), 400
    
    try:
        conn.execute('''
            INSERT INTO LeaseApplications (app_renter_id, app_property_id, status)
            VALUES (?, ?, ?)
        ''', (
            data['app_renter_id'], 
            data['app_property_id'], 
            data['status']
        ))
        conn.commit()
        last_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Application created successfully", "application_id": last_id}), 201

@app.route('/applications/<application_id>', methods=['PUT'])
def update_application(application_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    conn = get_db_connection()
    application = conn.execute('SELECT * FROM LeaseApplications WHERE application_id = ?', (application_id,)).fetchone()
    
    if application is None:
        conn.close()
        return jsonify({"error": "Application not found"}), 404
    
    if 'status' in data and len(data) == 1:
        try:
            conn.execute('UPDATE LeaseApplications SET status = ? WHERE application_id = ?', 
                         (data['status'], application_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            return jsonify({"error": str(e)}), 400
    else:
        update_fields = []
        values = []
        
        for field in ['app_renter_id', 'app_property_id', 'status']:
            if field in data:
                update_fields.append(f"{field} = ?")
                values.append(data[field])
        
        if not update_fields:
            conn.close()
            return jsonify({"error": "No fields to update"}), 400
        
        sql = f"UPDATE LeaseApplications SET {', '.join(update_fields)} WHERE application_id = ?"
        values.append(application_id)
        
        try:
            conn.execute(sql, values)
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.close()
            return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Application updated successfully"})

@app.route('/applications/<application_id>', methods=['DELETE'])
def delete_application(application_id):
    conn = get_db_connection()
    application = conn.execute('SELECT * FROM LeaseApplications WHERE application_id = ?', (application_id,)).fetchone()
    
    if application is None:
        conn.close()
        return jsonify({"error": "Application not found"}), 404
    
    try:
        conn.execute('DELETE FROM LeaseApplications WHERE application_id = ?', (application_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Application deleted successfully"})

# CRUD Operations for Reviews
@app.route('/reviews', methods=['GET'])
def get_reviews():
    conn = get_db_connection()
    reviews = conn.execute('''
        SELECT r.*, 
               renter.name as renter_name,
               CASE 
                   WHEN r.rev_property_id IS NOT NULL THEN p.property_name
                   ELSE NULL
               END as property_name,
               CASE 
                   WHEN r.rev_office_id IS NOT NULL THEN o.name
                   ELSE NULL
               END as office_name
        FROM Reviews r
        LEFT JOIN Renter renter ON r.rev_renter_id = renter.renter_id
        LEFT JOIN Property p ON r.rev_property_id = p.property_id
        LEFT JOIN LeasingOffice o ON r.rev_office_id = o.office_id
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(review) for review in reviews])

@app.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    conn = get_db_connection()
    review = conn.execute('''
        SELECT r.*, 
               renter.name as renter_name,
               CASE 
                   WHEN r.rev_property_id IS NOT NULL THEN p.property_name
                   ELSE NULL
               END as property_name,
               CASE 
                   WHEN r.rev_office_id IS NOT NULL THEN o.name
                   ELSE NULL
               END as office_name
        FROM Reviews r
        LEFT JOIN Renter renter ON r.rev_renter_id = renter.renter_id
        LEFT JOIN Property p ON r.rev_property_id = p.property_id
        LEFT JOIN LeasingOffice o ON r.rev_office_id = o.office_id
        WHERE r.review_id = ?
    ''', (review_id,)).fetchone()
    
    if review is None:
        conn.close()
        return jsonify({"error": "Review not found"}), 404
    
    conn.close()
    return jsonify(dict(review))

@app.route('/reviews', methods=['POST'])
def create_review():
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    required_fields = ['rev_renter_id', 'rating']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if not data.get('rev_property_id') and not data.get('rev_office_id'):
        return jsonify({"error": "Either rev_property_id or rev_office_id must be provided"}), 400
    
    conn = get_db_connection()
    
    try:
        conn.execute('''
            INSERT INTO Reviews (rev_renter_id, rev_property_id, rev_office_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['rev_renter_id'],
            data.get('rev_property_id'),
            data.get('rev_office_id'),
            data['rating'],
            data.get('comment')
        ))
        conn.commit()
        last_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Review created successfully", "review_id": last_id}), 201

@app.route('/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    if not request.json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.json
    
    conn = get_db_connection()
    review = conn.execute('SELECT * FROM Reviews WHERE review_id = ?', (review_id,)).fetchone()
    
    if review is None:
        conn.close()
        return jsonify({"error": "Review not found"}), 404
    
    update_fields = []
    values = []
    
    for field in ['rev_renter_id', 'rev_property_id', 'rev_office_id', 'rating', 'comment']:
        if field in data:
            update_fields.append(f"{field} = ?")
            values.append(data[field])
    
    if not update_fields:
        conn.close()
        return jsonify({"error": "No fields to update"}), 400
    
    sql = f"UPDATE Reviews SET {', '.join(update_fields)} WHERE review_id = ?"
    values.append(review_id)
    
    try:
        conn.execute(sql, values)
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Review updated successfully"})

@app.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    conn = get_db_connection()
    review = conn.execute('SELECT * FROM Reviews WHERE review_id = ?', (review_id,)).fetchone()
    
    if review is None:
        conn.close()
        return jsonify({"error": "Review not found"}), 404
    
    try:
        conn.execute('DELETE FROM Reviews WHERE review_id = ?', (review_id,))
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify({"success": True, "message": "Review deleted successfully"})

# endpoint
@app.route('/properties/budget/<min_price>/<max_price>', methods=['GET'])
def get_properties_by_budget(min_price, max_price):
    conn = get_db_connection()
    
    try:
        properties = conn.execute('SELECT * FROM Property WHERE price_per_person BETWEEN ? AND ?', 
                                  (min_price, max_price)).fetchall()
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": str(e)}), 400
    
    conn.close()
    return jsonify([dict(property) for property in properties])

# Run
if __name__ == '__main__':
    app.run(debug=True)