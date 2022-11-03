from flask_jwt_extended import jwt_required
from app import logging
from flask import Blueprint, jsonify, request
from app.logics import concerts
from app.static.exceptions import KeyNotFound

logger = logging.getLogger()
concert_routes = Blueprint("concert_routes", __name__)

@concert_routes.route('/concerts/new', methods=['POST'])
def create_new_concert():
    try:
        concerts.create_new_concert(request.get_json(force=True))
        return jsonify({"status": True, "data": "Concert added"})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

# @jwt_required() -- not working when only here
@concert_routes.route('/concerts/<int:id>')
def get_concert_details(id):
    try:
        concert_dto = concerts.get_concert_details(id)
        return jsonify({"status": True, "data": concert_dto.asdict()})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@jwt_required()
@concert_routes.route('/concerts/<int:id>/seats', methods=['POST'])
def create_concert_seating_plan(id):
    try:
        seating_plan = concerts.create_seating_plan_for_concert(id, request.get_json(force=True))
        return jsonify({"status": True, "data": seating_plan})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@jwt_required()
@concert_routes.route('/concerts/<int:id>/buy_tickets', methods=['POST'])
def buy_concert_tickets(id):
    try:
        result = concerts.buy_tickets(id, request.get_json(force=True))
        return jsonify({"status": True, "data": result})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@jwt_required()
@concert_routes.route('/concerts/<int:id>/seats')
def get_concert_seats_details(id):
    try:
        concert_seats_dto = concerts.get_seating_plan_for_concert(id)
        return jsonify({"status": True, "data": concert_seats_dto.asdict()})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@jwt_required()
@concert_routes.route('/concerts/<int:id>', methods=['POST'])
def save_tickets(id):
    try:
        concerts.save_tickets(id, request.get_json(force=True))
        return jsonify({"status": True})
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503