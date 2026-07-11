from dataclasses import dataclass
import re
from app.domain.exceptions.auth_errors import InvalidDNIError

@dataclass(frozen=True)
class DNI:
    value: str

    def __post_init__(self) -> None:
        if not self.value or not re.match(r"^\d{8}$", self.value):
            raise InvalidDNIError("DNI must be exactly 8 digits.")
