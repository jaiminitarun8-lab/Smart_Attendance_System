import hashlib


def hash_password(password: str) -> str:
    """Password ko hash (encrypt) karta hai — database me plain text kabhi save nahi karte."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Login ke time entered password ko database ke hash se compare karta hai."""
    return hash_password(plain_password) == hashed_password
