# International Bank Account Number
from dataclasses import dataclass
import re
from app.domain.exceptions.auth_errors import InvalidIBANError

@dataclass(frozen=True)
class IBAN:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise InvalidIBANError("IBAN cannot be empty.")
        
        clean_value = self.value.replace(" ", "").upper()
        # Basic format check: Country code (2 letters) + 2 digits + 11 to 30 alphanumeric characters
        pattern = r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$"
        if not re.match(pattern, clean_value):
            raise InvalidIBANError(f"Invalid IBAN format: {self.value}")
        
        # MOD-97 checksum validation
        check_str = clean_value[4:] + clean_value[:4]
        num_str = "".join(str(int(char, 36)) if char.isalpha() else char for char in check_str)
        if int(num_str) % 97 != 1:
            raise InvalidIBANError(f"Invalid IBAN checksum: {self.value}")
        
        # Override the field with normalized value
        object.__setattr__(self, "value", clean_value)
