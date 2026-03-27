"""
utils/validator.py
Coupon-code input validation using regex.
"""

import re

# Coupon codes for FC Online / Garena are typically:
#   – alphanumeric only
#   – between 6 and 32 characters
#   – may contain hyphens as separators (e.g. XXXX-XXXX-XXXX)
_COUPON_PATTERN = re.compile(r"^[A-Za-z0-9\-]{6,32}$")

# Maximum raw message length we will even attempt to validate (safety)
_MAX_RAW_LENGTH = 64


def is_valid_coupon(code: str) -> bool:
    """
    Return True if *code* looks like a valid coupon code.

    Rules:
    - Must be a non-empty string
    - Stripped length 6–32 characters
    - Only alphanumeric characters and hyphens allowed
    """
    if not isinstance(code, str):
        return False
    code = code.strip()
    if not code or len(code) > _MAX_RAW_LENGTH:
        return False
    return bool(_COUPON_PATTERN.match(code))


def sanitize(code: str) -> str:
    """
    Normalise a coupon code string:
    - Strip whitespace
    - Convert to upper-case
    """
    return code.strip().upper()
