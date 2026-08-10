class ApplicationError(Exception):
    pass

class ValidationError(ApplicationError):
    pass

class NotFoundError(ApplicationError):
    pass

class ConflictError(ApplicationError):
    pass

class AuthenticationError(ApplicationError):
    pass

class AuthorizationError(ApplicationError):
    pass

class RateLimitError(ApplicationError):
    def __init__(
        self,
        message: str,
        retry_after: int,
    ):
        super().__init__(message)
        self.retry_after = retry_after