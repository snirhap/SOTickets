from dataclasses import dataclass
from app.dto_models.base import BaseDTO

@dataclass 
class BaseAisleDTO(BaseDTO):
    gate_id: int
    aisle_number: int

@dataclass 
class AisleDTO(BaseAisleDTO):
    id: int
    seats: list