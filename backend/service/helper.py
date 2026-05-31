import os 
import re
from datetime import datetime 

def validate_date_format(date_string: str) ->str:
    """Custom type validator for YYYY-MM-DD format."""
    if date_string is None:
        return
    return datetime.strptime(date_string, '%Y-%m-%d').date()


def validate_credential(data: dict):
    """
    {
        "email": str,
        "password": str,
        "phone_no": str,
    }
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", data["email"]):
        raise ValueError("Invalid email format")
    
    if not len(data["password"]) >= 8:
        raise ValueError("Password must be more then 8 characters long")

    if not len(data["phone_no"]) >= 10:
        raise ValueError("Phone number should be at least 10 number long.")
          

