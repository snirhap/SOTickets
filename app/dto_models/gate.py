from dataclasses import dataclass
from app.db_models.gate import SeatingType
from app.dto_models.base import BaseDTO

@dataclass 
class BaseGateDTO(BaseDTO):
    concert_id: int
    seating_type: SeatingType
    number_of_seats: int
    gate_number: int

@dataclass 
class GateDTO(BaseGateDTO):
    id: int
    aisles: list