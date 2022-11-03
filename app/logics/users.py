import re
import io
import csv
from random import randint
from app import app, logging
from datetime import timedelta
from flask_jwt_extended import create_access_token
from app.db_actions import users as user_db_actions
from app.dto_models.user import UserDTO
from werkzeug.security import generate_password_hash, check_password_hash
from app.static.exceptions import *
from app import redis_manager, mail
from flask_mail import Message

logger = logging.getLogger()
ALLOWED_EXTENSIONS = {'csv'}

def get_all_users():
    all_users = {}
    users = user_db_actions.query_all_table()
    for i, user in enumerate(users):
        all_users[i] = {"email": user.email, 
                        "username": user.username, 
                        "password": user.password}
    return all_users

def register(request_data: dict):
    try:
        new_user = UserDTO(email=request_data["email"],
                            username=request_data["username"],
                            password=generate_password_hash(request_data["password"]))

        if bool(user_db_actions.get_user(new_user)):
            logger.error(f'User {new_user.username} already exists')
            raise UserRegisterationError('User already exists')

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', new_user.email):
            raise UserRegisterationError('Invalid email address!')
        elif not re.match("^[a-zA-Z]([._-]?[a-zA-Z0-9]+)*$", new_user.username):
            raise UserRegisterationError('Username must start and end with a letter and contain only characters, numbers, "_", "-" !')
        elif not new_user.username or not new_user.password or not new_user.email:
            raise UserRegisterationError('Please fill out the form !')
        
        # If all is good, Pass to db_actions.register
        user_db_actions.insert_new_user(new_user)
    except UserRegisterationError as err:
        logger.error(f'Error while register new user: {new_user}. Error: {err.message}')
        raise
    except Exception as err:
        logger.error(f'Error while register: {err}')
        raise

def register_bulk(new_users_list: list):
    check_users = user_db_actions.get_all_users_by_list_of_usernames([user["username"] for user in new_users_list])
    if check_users:
        logger.error(f'Should remove existing users from request {check_users}')
        raise UserRegisterationError(check_users)
    else:
        # bulk insert users
        for user in new_users_list:
            register(user)
        logger.info('OK')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_with_file(file):
    if file.filename != '' and allowed_file(file.filename):
        with io.TextIOWrapper(file) as fp:
            reader = csv.DictReader(fp, delimiter=',')
            register_bulk([user for user in reader])
    else:
        raise UserLoginError('No files were sent')

def login(request_data: dict):
    try:
        user_data = UserDTO(email=request_data["email"],
                            username=request_data["username"],
                            password=request_data["password"])
        db_user = user_db_actions.get_user(user_data)
        if db_user and check_password_hash(db_user.password, user_data.password):
            otp = randint(11111,99999)
            redis_manager.set_key_value(db_user.id, otp, app.config["OTP_EXPIRY_SECONDS"])
            msg = Message('SOTickets - OTP', sender = app.config["MAIL_USERNAME"], recipients = [user_data.email])
            msg.body = f"OTP: {otp}"
            mail.send(msg)            
        else:
            raise UserLoginError('Check your credentials')
    except Exception as err:
        logger.error(f'Error while login: {err}')
        raise

def verify_otp(request_data: dict):
    try:
        user_data = UserDTO(username=request_data["username"])
        otp_provided = request_data["otp"]
        db_user = user_db_actions.get_user(user_data)
        app.logger.info(f'db_user: {db_user}')
        if db_user:
            generated_otp = redis_manager.get_value_by_key(db_user.id)
            app.logger.info(f'generated_otp: {generated_otp}')
            app.logger.info(f'otp_provided: {otp_provided}')
            if generated_otp and generated_otp == otp_provided:
                app.logger.info(f'User {db_user.username} was verified thru OTP')
                access_token = create_access_token(identity=db_user.username, expires_delta=timedelta(minutes=app.config["JWT_EXPIRATION_MINUTES"]))
                app.logger.info(f'Created access token: {access_token}')
                return access_token
            else:
                app.logger.error(f'Wrong OTP for user {db_user.username}')
                raise UserOTPError("Wrong OTP")
        else:
            app.logger.error(f'{db_user.username} does not exist')
            raise UserOTPError("User not exist")
    except KeyNotFound as err:
        logger.error(f'There is no record of OTP for user {user_data.username}')
        raise
    except Exception as err:
        logger.error(f'Error while otp: {err}')
        raise
