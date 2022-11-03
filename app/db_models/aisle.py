from app import db

class Aisle(db.Model):
    __tablename__ = "aisles"
    id = db.Column(db.Integer, primary_key=True)
    gate_id = db.Column(db.Integer, db.ForeignKey("gates.id"), nullable=False)
    gate = db.relationship("Gate", foreign_keys=gate_id, back_populates="aisles")
    aisle_number = db.Column(db.Integer)

    seats = db.relationship("Seat", back_populates="aisle")

    def __init__(self, gate_id, aisle_number) -> None:
        self.gate_id = gate_id
        self.aisle_number = aisle_number
