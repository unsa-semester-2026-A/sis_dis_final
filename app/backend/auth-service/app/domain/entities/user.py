from dataclasses import dataclass
from datetime import datetime
import re

from app.domain.value_objects.dni import DNI
from app.domain.value_objects.email import Email
from app.domain.value_objects.iban import IBAN
from app.domain.value_objects.password import Password
from app.domain.value_objects.phone_number import PhoneNumber


# from app.domain.exceptions.auth_errors import InvalidEmailError, PasswordTooWeakError


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
    pin_salt: str
    created_at: datetime
    updated_at: datetime
