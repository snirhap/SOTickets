from flask_jwt_extended import jwt_required
from app import logging
from flask import Blueprint, jsonify, request
from app.logics import bands
from app.static.exceptions import KeyNotFound

logger = logging.getLogger()
bands_routes = Blueprint("bands_routes", __name__)

@bands_routes.route('/bands')
def get_all_bands():
    try:
        all_bands_list = bands.get_all_bands()
        return jsonify({"status": True, "data": all_bands_list})
    except Exception as err:
        return jsonify({"status": False, "message": str(err)})

@bands_routes.route('/bands/<id>')
def get_band_data(id):
    try:
        band_details = bands.get_band_details(id)
        return jsonify({"status": True, "data": band_details})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@jwt_required()
@bands_routes.route('/bands/<id>/concerts')
def get_band_concerts(id):
    try:
        band_concerts = bands.get_band_concerts(id)
        return jsonify({"status": True, "data": band_concerts})
    except KeyNotFound as err:
        return jsonify({"status": False, "message": str(err)}), 401
    except Exception as err:
        return jsonify({"status": False, "message": str(err)}), 503

@bands_routes.route('/bands/new', methods=["POST"])
def insert_new_band():
    try:
        bands.insert_new_band(request.get_json(force=True))
        return jsonify({"message": "Band added to DB"})
    except Exception as err:
        return jsonify({"message": str(err)}), 503