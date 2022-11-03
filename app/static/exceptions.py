class KeyNotFound(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)

class UserRegisterationError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)

class UserLoginError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)

class UserOTPError(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)