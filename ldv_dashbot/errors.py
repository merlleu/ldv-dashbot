class AuthError(BaseException):
    def __init__(self, s): self.s = s
    def __repr__(self): return self.s

class NotAuthenticatedError(BaseException):pass
class InvalidCredentials(BaseException):pass
class UnsuccessfullResponse(BaseException):
    def __init__(self, r): self.r = r


class PresenceClassNotFound(BaseException):pass