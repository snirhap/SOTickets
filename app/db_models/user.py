from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True, nullable=False)
    email = db.Column(db.String(150), index=True, unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    tickets = db.relationship("Ticket", back_populates="user")

    def __init__(self, email, username, password) -> None:
        self.email = email
        self.username = username
        self.password = password
