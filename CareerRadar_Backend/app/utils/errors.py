"""API exceptions with consistent JSON error details."""


class ApiError(Exception):
    def __init__(self, code, message, status_code):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class ValidationError(ApiError):
    def __init__(self, message, code="VALIDATION_ERROR"):
        super().__init__(code, message, 400)


class UnauthorizedError(ApiError):
    def __init__(self, message="Authentication required."):
        super().__init__("UNAUTHORIZED", message, 401)


class ForbiddenError(ApiError):
    def __init__(self, message="You do not have permission to perform this action."):
        super().__init__("FORBIDDEN", message, 403)


class NotFoundError(ApiError):
    def __init__(self, message="The requested resource was not found.", code="NOT_FOUND"):
        super().__init__(code, message, 404)


class ConflictError(ApiError):
    def __init__(self, message="The request conflicts with existing data.", code="CONFLICT"):
        super().__init__(code, message, 409)
