from app import db

class Band(db.Model):
    __tablename__ = 'bands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True, unique=True, nullable=False)
    date_formed = db.Column(db.Date)
    genre = db.Column(db.String(50), nullable=False)
    concerts = db.relationship("Concert", back_populates="band", cascade="all, delete", passive_deletes=True)

    def __init__(self, name, date_formed, genre) -> None:
        self.name = name
        self.date_formed = date_formed
        self.genre = genre
