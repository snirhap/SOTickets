from dataclasses import dataclass
from app.dto_models.base import BaseDTO

@dataclass
class UserDTO(BaseDTO):
    username: str
    email: str = None
    password: str = None