from dataclasses import dataclass
import datetime
from app.dto_models.base import BaseDTO

@dataclass
class BandDTO(BaseDTO):
    name: str
    date_formed: datetime
    genre: str