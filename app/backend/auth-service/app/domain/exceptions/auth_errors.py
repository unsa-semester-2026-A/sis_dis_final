class AuthDomainError(ValueError):
    """Base exception class for authentication domain errors."""
    pass

class InvalidDNIError(AuthDomainError):
    """Raised when a DNI is invalid."""
    pass

class InvalidEmailError(AuthDomainError):
    """Raised when an email address is invalid."""
    pass

class InvalidPhoneNumberError(AuthDomainError):
    """Raised when a phone number is invalid."""
    pass

class PasswordTooWeakError(AuthDomainError):
    """Raised when a password does not meet security requirements."""
    pass
