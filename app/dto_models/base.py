from dataclasses import dataclass, asdict

@dataclass 
class BaseDTO:

    def asdict(self):
        return asdict(self)
