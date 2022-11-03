from app import db

class Seat(db.Model):
    __tablename__ = "seats"
    id = db.Column(db.Integer, primary_key=True)
    aisle_id = db.Column(db.Integer, db.ForeignKey("aisles.id"), nullable=False)
    aisle = db.relationship("Aisle", foreign_keys=aisle_id, back_populates="seats")
    seat_number = db.Column(db.Integer)
    available = db.Column(db.Boolean, unique=False, default=True)
    price = db.Column(db.Integer, unique=False)

    ticket = db.relationship("Ticket", back_populates="seat", uselist=False)

    def __init__(self, aisle_id, seat_number, available, price) -> None:
        self.aisle_id = aisle_id
        self.seat_number = seat_number
        self.available = available
        self.price = price
