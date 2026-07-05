from dataclasses import dataclass

@dataclass
class PhoneNumber:
    country_code: str
    number: str