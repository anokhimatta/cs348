import sqlite3
from flask import Flask, request, jsonify, g
from flask import CORS
import os
app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'apartments.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False, commit=False):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
        if one:
            return cursor.fetchone()
        return cursor.fetchall()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

def dict_from_row(row):
    return {k: row[k] for k in row.keys()} if row else None 

# PROPERTY CRUD
@app.route('/api/properties', methods=['GET'])
def get_properties():
    try:
        sql = """
        SELECT * FROM Property
        """
        rows = query_db(sql)
        properties = [dict_from_row(row) for row in rows]
        return jsonify(properties)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    try:
        sql = """
        SELECT * FROM Property WHERE id = ?
        """
        row = query_db(sql, (id,), one=True)
        if not row:
            return jsonify({"error": "Property not found"}), 404
        return jsonify(dict_from_row(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/properties', methods=['POST'])
def create_property():
    try:
        data = request.get_json()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"""
        INSERT INTO Property ({columns})
        VALUES ({placeholders})
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        property_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Property added", "id": property_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    try:
        data = request.get_json()
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(id)  # For the WHERE clause
        
        sql = f"""
        UPDATE Property 
        SET {set_clause}
        WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Property not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Property updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    try:
        sql = """
        DELETE FROM Property WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Property not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Property deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# RENTER CRUD
@app.route('/api/renters', methods=['GET'])
def get_renters():
    try:
        sql = """
        SELECT * FROM Renter
        """
        rows = query_db(sql)
        renters = [dict_from_row(row) for row in rows]
        return jsonify(renters)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/renters/<int:id>', methods=['GET'])
def get_renter(id):
    try:
        sql = """
        SELECT * FROM Renter WHERE id = ?
        """
        row = query_db(sql, (id,), one=True)
        if not row:
            return jsonify({"error": "Renter not found"}), 404
        return jsonify(dict_from_row(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/renters', methods=['POST'])
def create_renter():
    try:
        data = request.get_json()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"""
        INSERT INTO Renter ({columns})
        VALUES ({placeholders})
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        renter_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Renter added", "id": renter_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/renters/<int:id>', methods=['PUT'])
def update_renter(id):
    try:
        data = request.get_json()
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(id)  # For the WHERE clause
        
        sql = f"""
        UPDATE Renter 
        SET {set_clause}
        WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Renter not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Renter updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/renters/<int:id>', methods=['DELETE'])
def delete_renter(id):
    try:
        sql = """
        DELETE FROM Renter WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Renter not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Renter deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LEASING OFFICE CRUD
@app.route('/api/leasing-offices', methods=['GET'])
def get_leasing_offices():
    try:
        sql = """
        SELECT * FROM "Leasing Office"
        """
        rows = query_db(sql)
        offices = [dict_from_row(row) for row in rows]
        return jsonify(offices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leasing-offices/<int:id>', methods=['GET'])
def get_leasing_office(id):
    try:
        sql = """
        SELECT * FROM "Leasing Office" WHERE id = ?
        """
        row = query_db(sql, (id,), one=True)
        if not row:
            return jsonify({"error": "Leasing Office not found"}), 404
        return jsonify(dict_from_row(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leasing-offices', methods=['POST'])
def create_leasing_office():
    try:
        data = request.get_json()
        columns = ', '.join([f'"{key}"' for key in data.keys()])  # Quote column names
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"""
        INSERT INTO "Leasing Office" ({columns})
        VALUES ({placeholders})
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        office_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Leasing Office added", "id": office_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leasing-offices/<int:id>', methods=['PUT'])
def update_leasing_office(id):
    try:
        data = request.get_json()
        set_clause = ', '.join([f'"{key}" = ?' for key in data.keys()])  # Quote column names
        values = list(data.values())
        values.append(id)  # For the WHERE clause
        
        sql = f"""
        UPDATE "Leasing Office" 
        SET {set_clause}
        WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Leasing Office not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Leasing Office updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leasing-offices/<int:id>', methods=['DELETE'])
def delete_leasing_office(id):
    try:
        sql = """
        DELETE FROM "Leasing Office" WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Leasing Office not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Leasing Office deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# LEASE APPLICATIONS CRUD
@app.route('/api/lease-applications', methods=['GET'])
def get_lease_applications():
    try:
        sql = """
        SELECT * FROM "Lease Application"
        """
        rows = query_db(sql)
        applications = [dict_from_row(row) for row in rows]
        return jsonify(applications)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lease-applications/<int:id>', methods=['GET'])
def get_lease_application(id):
    try:
        sql = """
        SELECT * FROM "Lease Application" WHERE id = ?
        """
        row = query_db(sql, (id,), one=True)
        if not row:
            return jsonify({"error": "Lease Application not found"}), 404
        return jsonify(dict_from_row(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lease-applications', methods=['POST'])
def create_lease_application():
    try:
        data = request.get_json()
        columns = ', '.join([f'"{key}"' for key in data.keys()])  # Quote column names
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"""
        INSERT INTO "Lease Application" ({columns})
        VALUES ({placeholders})
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        application_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Lease Application added", "id": application_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lease-applications/<int:id>', methods=['PUT'])
def update_lease_application(id):
    try:
        data = request.get_json()
        set_clause = ', '.join([f'"{key}" = ?' for key in data.keys()])  # Quote column names
        values = list(data.values())
        values.append(id)  # For the WHERE clause
        
        sql = f"""
        UPDATE "Lease Application" 
        SET {set_clause}
        WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Lease Application not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Lease Application updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lease-applications/<int:id>', methods=['DELETE'])
def delete_lease_application(id):
    try:
        sql = """
        DELETE FROM "Lease Application" WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Lease Application not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Lease Application deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# REVIEWS CRUD
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    try:
        sql = """
        SELECT * FROM Reviews
        """
        rows = query_db(sql)
        reviews = [dict_from_row(row) for row in rows]
        return jsonify(reviews)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:id>', methods=['GET'])
def get_review(id):
    try:
        sql = """
        SELECT * FROM Reviews WHERE id = ?
        """
        row = query_db(sql, (id,), one=True)
        if not row:
            return jsonify({"error": "Review not found"}), 404
        return jsonify(dict_from_row(row))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews', methods=['POST'])
def create_review():
    try:
        data = request.get_json()
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = tuple(data.values())
        
        sql = f"""
        INSERT INTO Reviews ({columns})
        VALUES ({placeholders})
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        review_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Review added", "id": review_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:id>', methods=['PUT'])
def update_review(id):
    try:
        data = request.get_json()
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(id)
        
        sql = f"""
        UPDATE Reviews 
        SET {set_clause}
        WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, values)
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Review not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Review updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reviews/<int:id>', methods=['DELETE'])
def delete_review(id):
    try:
        sql = """
        DELETE FROM Reviews WHERE id = ?
        """
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        
        if cursor.rowcount == 0:
            conn.rollback()
            cursor.close()
            return jsonify({"error": "Review not found"}), 404
        
        conn.commit()
        cursor.close()
        
        return jsonify({"message": "Review deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)