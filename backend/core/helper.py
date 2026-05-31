import os
from datetime import datetime 
import pytz

def load_env(filepath: str):
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip("'").strip('"')
                    
                    os.environ[key] = value 
    except FileNotFoundError:
        print(f"Warning: {filepath} not found.")


def IndiaTimeStampNow():
    """
    Returns the current datetime object in India (Asia/Kolkata)
    """
    IST = pytz.timezone('Asia/Kolkata')
    return datetime.now(IST)
