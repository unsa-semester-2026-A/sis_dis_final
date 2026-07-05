from dataclasses import dataclass
import re
from app.domain.exceptions.auth_errors import InvalidPhoneNumberError

@dataclass(frozen=True)
class PhoneNumber:
    country_code: str
    number: str

    def __post_init__(self) -> None:
        if not self.country_code or not re.match(r"^\+\d{1,4}$", self.country_code):
            raise InvalidPhoneNumberError(f"Invalid country code: {self.country_code}")
        if not self.number or not re.match(r"^\d{7,15}$", self.number):
            raise InvalidPhoneNumberError(f"Invalid phone number: {self.number}")