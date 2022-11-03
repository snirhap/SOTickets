from dataclasses import dataclass
from app.dto_models.base import BaseDTO

@dataclass 
class BaseTicketDTO(BaseDTO):
    user_id: int
    seat_id: int
    price: int

@dataclass 
class TicketDTO(BaseTicketDTO):
    id: int