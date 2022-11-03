from dataclasses import dataclass
from datetime import datetime
from app.dto_models.base import BaseDTO


@dataclass
class BaseConcertDTO(BaseDTO):
    band_id: int
    date: datetime
    tickets_available: int

@dataclass
class ConcertDTO(BaseConcertDTO):
    concert_id: int
    band_name: str
    seating_types: list

@dataclass
class SeatingPlanDTO(BaseDTO):
    number_purchased_tickets: int
    number_of_available_tickets: int
    gates: list