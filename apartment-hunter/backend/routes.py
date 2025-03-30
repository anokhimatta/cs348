from flask import Blueprint, jsonify
from models import db, LeaseApplications

routes = Blueprint("routes", __name__)

@routes.route('/leases', methods=['GET'])
def get_leases():
    leases = LeaseApplications.query.all()
    leases_list = [
        {"id": lease.application_id, "status": lease.status}
        for lease in leases
    ]
    return jsonify(leases_list)