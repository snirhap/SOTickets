from datetime import datetime
from app import logging
from app.db_actions import bands as bands_db_actions
from app.dto_models.band import BandDTO
from app.static.exceptions import KeyNotFound

logger = logging.getLogger()

def get_all_bands():
    all_bands = bands_db_actions.query_all_table()
    return [{"id": band.id, "name": band.name} for band in all_bands]

def get_band_details(band_id: int):
    try:
        band = bands_db_actions.get_band_details(band_id)
        if band:
            band_dto = BandDTO(band.name, band.date_formed, band.genre)
            return band_dto
        else:
            raise KeyNotFound(f"Band doesn't exist")
    except Exception as err:
        logger.error(err)
        raise

def get_band_concerts(band_id: int):
    try:
        band = bands_db_actions.get_band_details(band_id)
        if band:
            band_concerts = bands_db_actions.get_band_concerts(band_id)
            return [{"(concert) id": concert.id, "date": concert.date} for concert in band_concerts] 
        else:
            raise KeyNotFound("Band not exists")
    except Exception as err:
        logger.error(err)
        raise 

def insert_new_band(request_data: dict):
    try:
        band_name = request_data["name"]
        bandDTO = BandDTO(band_name, datetime.strptime(request_data["date_formed"], '%d/%m/%Y'), request_data["genre"])
        if not bands_db_actions.check_if_exists(band_name):
            bands_db_actions.insert_new_band(bandDTO)
        else:
            raise Exception(f"Band {bandDTO.name} already exists!")
    except Exception as err:
        logger.error(err)
        raise