class Response:
    def __init__(self, status: bool, message: str, data: dict = None, token: str = None) -> None:
        self.status = status
        self.message = message
        self.data = data
        self.token = token
    
    def as_dict(self):
            return {k: v for k, v in vars(self).items() if v is not None}