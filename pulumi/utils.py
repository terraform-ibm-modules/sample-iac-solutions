# Helper Methods

import random
import string


def generate_suffix(length: int = 4) -> str:
    """Generate a random alphanumeric suffix for resource names."""
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def first_or_self(x):
    """Return first element if list, else return the value itself."""
    return x[0] if isinstance(x, list) else x
