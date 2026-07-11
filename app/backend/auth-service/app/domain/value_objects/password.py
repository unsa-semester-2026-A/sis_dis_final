from dataclasses import dataclass
from app.domain.exceptions.auth_errors import PasswordTooWeakError

@dataclass(frozen=True)
class Password:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise PasswordTooWeakError("Password cannot be empty.")
        if len(self.value) < 8:
            raise PasswordTooWeakError("Password must be at least 8 characters long.")
        if not any(char.isupper() for char in self.value):
            raise PasswordTooWeakError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in self.value):
            raise PasswordTooWeakError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in self.value):
            raise PasswordTooWeakError("Password must contain at least one digit.")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for char in self.value):
            raise PasswordTooWeakError("Password must contain at least one special character.")
