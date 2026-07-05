from dataclasses import dataclass
import re
from app.domain.exceptions.auth_errors import InvalidEmailError

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not self.value or not re.match(pattern, self.value):
            raise InvalidEmailError(f"Invalid email address: {self.value}")
