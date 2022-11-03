import logging
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.logics import users
from app.static.exceptions import *
from app.static.response import Response

logger = logging.getLogger()
users_routes = Blueprint("users_routes", __name__)

@users_routes.route('/register', methods=['POST'])
def register():
    try:
        users.register(request.get_json(force=True))
        return jsonify(Response(True, 'User added!').as_dict()), 201
    except UserRegisterationError as err:
        return jsonify(Response(False, err.message).as_dict()), 401
    except Exception as err:
        return jsonify(Response(False, f'Problem with user registration: {err}').as_dict()), 503

@users_routes.route('/register_bulk', methods=['POST'])
def register_bulk():
    try:
        users.register_bulk(request.get_json(force=True))
        return jsonify(Response(True, 'OK').as_dict())
    except UserRegisterationError as err:
        return jsonify(Response(False, f'Should remove existing users from request: {err.message}').as_dict()), 449
    except Exception as err:
        return jsonify(Response(False, f'Problem with user registration: {err}').as_dict()), 503

@users_routes.route('/register_from_file', methods=['POST'])
def register_via_csv():
    try:
        users.register_with_file(request.files['file'])
        return jsonify(Response(True, 'OK').as_dict())
    except UserRegisterationError as err:
        return jsonify(Response(False, f'Should remove existing users from request: {err.message}').as_dict()), 449
    except Exception as err:
        return jsonify(Response(False, f"Problem with user registration: {err}").as_dict()), 503

@users_routes.route('/login', methods=['POST'])
def login():
    try:
        users.login(request.get_json(force=True))
        return jsonify(Response(True, "Sent an otp to the email provided").as_dict()), 200
    except UserLoginError as err:
        return jsonify(Response(False, err.message).as_dict()), 401
    except Exception as err:
        return jsonify(Response(False, f"Problem with user login: {err}").as_dict()), 503

@users_routes.route('/otp', methods=['POST'])
def verify_otp():
    try:
        token = users.verify_otp(request.get_json(force=True))
        logger.info(f'token: {token}')
        return jsonify(Response(True, "OK", token=token).as_dict()), 200
    except (KeyNotFound, UserOTPError) as err:
        return jsonify(Response(False, f"OTP expired or user doesn't exist: {err}").as_dict()), 401
    except Exception as err:
        logger.error(err)
        return jsonify(Response(False, f"Problem with user otp verification: {err}").as_dict()), 503

@users_routes.route('/get_all_users')
def get_users():
    return users.get_all_users()
