from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plaintext: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return _pwd_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return _pwd_context.verify(plaintext, hashed)
