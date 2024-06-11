import re


# Custom validation functions
def validate_ip(value):
    # Check if the value is a valid IP address
    return re.match(r'^\d{1,3}(\.\d{1,3}){3}$', value) is not None


def validate_port(value):
    # Check if the value is a valid port (numeric and <= 5 characters)
    return value.isdigit() and len(value) <= 5


def validate_projector_id(value):
    # Check if the value is exactly 2 numerical characters
    return re.match(r'^\d{2}$', value) is not None


def get_last_int(s):
    for i in range(len(s) - 1, -1, -1):
        if not s[i:].isdigit():
            return int(s[i + 1:]) if i < len(s) - 1 else None
    return int(s)
