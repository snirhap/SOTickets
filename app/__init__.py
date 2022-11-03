import os
import logging
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager

app = Flask(__name__)

app.config.from_object('config')

# Modify config according to env vars
def update_config():
    if os.getenv('MYSQL_ROOT_USER') and os.getenv('MYSQL_ROOT_PASSWORD'):
        app.config.update({"SQLALCHEMY_DATABASE_URI": f"mysql+mysqlconnector://{os.getenv('MYSQL_ROOT_USER')}:{os.getenv('MYSQL_ROOT_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DATABASE')}"})
   
    app.config.update({"MAIL_SERVER": os.getenv('MAIL_SERVER')}) if os.getenv('MAIL_SERVER') else None
    app.config.update({"MAIL_PORT": os.getenv('MAIL_PORT')}) if os.getenv('MAIL_PORT') else None
    app.config.update({"MAIL_USERNAME": os.getenv('MAIL_USERNAME')}) if os.getenv('MAIL_USERNAME') else None
    app.config.update({"MAIL_PASSWORD": os.getenv('MAIL_PASSWORD')}) if os.getenv('MAIL_PASSWORD') else None
    
    app.config.update({"JWT_SECRET_KEY": os.getenv('JWT_SECRET_KEY')}) if os.getenv('JWT_SECRET_KEY') else None


update_config()

logging.basicConfig(filename=app.config["LOG_FILE"],
                    level=app.config["LOG_LEVEL"], 
                    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


# MySQL and DB models init
db = SQLAlchemy(app)
from app.db_models.user import User
from app.db_models.band import Band
from app.db_models.concert import Concert
from app.db_models.gate import Gate
from app.db_models.aisle import Aisle
from app.db_models.seat import Seat
from app.db_models.ticket import Ticket
time.sleep(10)
db.create_all()
app.logger.info('Connected to DB')

# Redis init
from app.cache.redis_manager import RedisManager
redis_manager = RedisManager(app.config["REDIS_HOST"], app.config["REDIS_PORT"])
app.logger.info('Connected to Redis')

# Email sender
mail = Mail(app)

# JWT 
jwt = JWTManager(app)

# Import controllers
from app.controllers.users import users_routes
from app.controllers.bands import bands_routes
from app.controllers.concerts import concert_routes

# Register blueprint(s)
app.register_blueprint(users_routes)
app.register_blueprint(bands_routes)
app.register_blueprint(concert_routes)

app.logger.info('Ready')
