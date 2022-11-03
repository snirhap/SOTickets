from app import db, logging
from app.db_models.gate import Gate
from app.db_models.aisle import Aisle
from app.db_models.seat import Seat


logger = logging.getLogger()

def query_all_gates_table():
    return Gate.query.all()

def get_gate_details(gate_id: int):
    return Gate.query.filter_by(id=gate_id).first()

def get_concert_gates(**filters):
    return Gate.query.filter_by(**filters).all()

def get_gate_seating_type(gate_id: int):
    return Gate.query.with_entities(Gate.seating_type).filter_by(id=gate_id).first()

def get_concert_gate_seating_types(concert_id: int):
    return Gate.query.with_entities(Gate.seating_type).distinct(Gate.seating_type).filter_by(concert_id=concert_id).all()

def get_gate_aisles(gate_ids_list: list):
    return Aisle.query.filter(Aisle.gate_id.in_(gate_ids_list)).all()

def get_seat_details(seat_id: int, **filters):
    return Seat.query.filter_by(id=seat_id, **filters).first()

def get_aisle_free_seats(aisle_id: int):
    return Seat.query.filter_by(aisle_id=aisle_id).filter(Seat.available==True).all()

def get_available_seats_from_seats_list(seats_list: list):
    return Seat.query.filter(Seat.id.in_(seats_list) & Seat.available==True).all()

def update_seat_availability(seat_id: int, status: bool):
    seat = Seat.query.filter_by(id=seat_id).first()
    seat.available = status
    db.session.commit()

def create_gates(gates_list: list):
    db.session.bulk_insert_mappings(Gate, gates_list)
    db.session.commit()

def create_aisles(aisles_list: list):
    db.session.bulk_insert_mappings(Aisle, aisles_list)
    db.session.commit()

def create_seats(seats_list: list):
    db.session.bulk_insert_mappings(Seat, seats_list)
    db.session.commit()