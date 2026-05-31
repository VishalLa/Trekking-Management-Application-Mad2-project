import datetime

def validate_date_format(date_string: str) ->str:
    """Custom type validator for YYYY-MM-DD format."""
    if date_string is None:
        return
    return datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
