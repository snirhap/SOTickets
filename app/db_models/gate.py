from enum import IntEnum
from app import db
from sqlalchemy import Enum

class SeatingType(IntEnum):
    standing = 1
    seated = 2
    virtual = 3

class Gate(db.Model):
    __tablename__ = "gates"
    id = db.Column(db.Integer, primary_key=True)
    concert_id = db.Column(db.Integer, db.ForeignKey("concerts.id"), nullable=False)
    concert = db.relationship("Concert", foreign_keys=concert_id, back_populates="gates")
    seating_type = db.Column(Enum(SeatingType))
    number_of_seats = db.Column(db.Integer)
    gate_number = db.Column(db.Integer)

    aisles = db.relationship("Aisle", back_populates="gate")

    def __init__(self, concert_id, seating_type, number_of_seats, gate_number) -> None:
        self.concert_id = concert_id
        self.seating_type = seating_type
        self.number_of_seats = number_of_seats
        self.gate_number = gate_number
    
    # def __repr__(self) -> str:
    #     return f'Concert ID: {self.id}; band: {self.band}; date: {self.date}; tickets_available: {self.tickets_available}'