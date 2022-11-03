from app import db

class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", foreign_keys=user_id, back_populates="tickets")

    seat_id = db.Column(db.Integer, db.ForeignKey("seats.id"))
    seat = db.relationship("Seat", back_populates="ticket")

    price = db.Column(db.Integer, unique=False)

    def __init__(self, aisle_id, seat_number, available, price) -> None:
        self.aisle_id = aisle_id
        self.seat_number = seat_number
        self.available = available
        self.price = price
    