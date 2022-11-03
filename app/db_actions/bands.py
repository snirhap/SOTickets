from app import db, logging
from app.db_models.band import Band
from app.db_models.concert import Concert
from app.dto_models.band import BandDTO
from datetime import datetime

logger = logging.getLogger()

def query_all_table():
    return Band.query.all()

def insert_new_band(band_dto: BandDTO):
    # new_band = Band(band_dto.name, datetime.strptime(band_dto.date_formed, '%d-%m-%Y').date(), band_dto.genre)
    new_band = Band(band_dto.name, band_dto.date_formed, band_dto.genre)
    db.session.add(new_band)
    db.session.commit()

def get_band_details(band_id: int):
    return Band.query.filter_by(id=band_id).first()

def check_if_exists(band_name: str):
    return bool(Band.query.filter_by(name=band_name).first())

def get_band_concerts(band_id: int):
    concerts = Concert.query.filter_by(band_id=band_id).all()
    return concerts