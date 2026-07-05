from dataclasses import dataclass
from app.domain.exceptions.auth_errors import PinLengthError, PinNotDigitsError

@dataclass(frozen=True)
class PIN:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise PinLengthError("PIN cannot be empty.")
        if not self.value.isdigit():
            raise PinNotDigitsError("PIN must contain only digits.")
        if len(self.value) != 6:
            raise PinLengthError("PIN must be exactly 6 digits long.")
