from app import db, logging
from app.db_models.user import User
from app.dto_models.user import UserDTO

logger = logging.getLogger()

def query_all_table():
    return User.query.all()

def insert_new_user(new_user_data: UserDTO):
    new_user = User(new_user_data.email, new_user_data.username, new_user_data.password)
    db.session.add(new_user)
    db.session.commit()

def get_user(user_data: UserDTO):
    return User.query.filter_by(username=user_data.username).first()

def get_user_by_username(user_id: int):
    return User.query.filter_by(username=user_id).first()

def get_all_users_by_list_of_usernames(user_names_list: list):
    return User.query.filter(User.username.in_(user_names_list)).all()
