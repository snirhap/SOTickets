from dataclasses import dataclass
from app.dto_models.base import BaseDTO

@dataclass 
class BaseSeatDTO(BaseDTO):
    aisle_id: int
    seat_number: int
    available: bool
    price: int

@dataclass 
class SeatDTO(BaseSeatDTO):
    id: int