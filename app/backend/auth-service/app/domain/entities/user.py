from dataclasses import dataclass
from datetime import datetime

from app.domain.value_objects.dni import DNI
from app.domain.value_objects.email import Email
#from app.domain.value_objects.password import Password
from app.domain.value_objects.phone_number import PhoneNumber

# the dataclass decorator make it like a record in java (generate getters, setters, constructors, toString)
@dataclass
class User:
    user_id: int
    DNI: DNI
    name: str
    last_name: str
    phone_number: PhoneNumber
    email: Email
    pin_hash: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty.")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name cannot be empty.")

    def update_email(self, new_email: Email) -> None:
        self.email = new_email
        self.updated_at = datetime.now()

    def update_phone_number(self, new_phone_number: PhoneNumber) -> None:
        self.phone_number = new_phone_number
        self.updated_at = datetime.now()

    def update_pin(self, pin_hash: str) -> None:
        if not pin_hash or not pin_hash.strip():
            raise ValueError("PIN hash cannot be empty.")
        self.pin_hash = pin_hash
        self.updated_at = datetime.now()

    def update_name(self, name: str, last_name: str) -> None:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        if not last_name or not last_name.strip():
            raise ValueError("Last name cannot be empty.")
        self.name = name.strip()
        self.last_name = last_name.strip()
        self.updated_at = datetime.now()
