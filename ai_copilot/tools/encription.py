"""One-way password hashing (the requested filename is kept for compatibility)."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Generate an Argon2id hash with a fresh random salt."""
    if not 15 <= len(password) <= 1024:
        raise ValueError("Password must contain between 15 and 1024 characters.")
    return _hasher.hash(password)


def verify_password(encoded: str, password: str) -> bool:
    if len(password) > 1024:
        return False
    try:
        return _hasher.verify(encoded, password)
    except VerificationError, InvalidHashError:
        return False


def needs_rehash(encoded: str) -> bool:
    return _hasher.check_needs_rehash(encoded)
