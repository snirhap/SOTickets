from app import db, logging
from app.db_models.concert import Concert
from app.db_models.gate import Gate
from datetime import datetime
from app.dto_models.concert import BaseConcertDTO

logger = logging.getLogger()

def create_concert(concert_dto: BaseConcertDTO):
    new_concert = Concert(concert_dto.band_id, concert_dto.date, concert_dto.tickets_available)
    db.session.add(new_concert)
    db.session.commit()

def query_all_table():
    return Concert.query.all()

def get_concert_details(concert_id: int):
    return Concert.query.filter_by(id=concert_id).first()

def get_concert_gates(concert_id: int):
    return Gate.query.filter_by(concert_id=concert_id).all()