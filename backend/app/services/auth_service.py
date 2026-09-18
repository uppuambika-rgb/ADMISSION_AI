"""
MongoDB-backed auth service.
Collections used:
  - users   : { email, name, password_hash, created_at }
  - tokens  : { token, email, expires_at }
"""
import hashlib
import hmac
import secrets
import time
from typing import Optional

from app.config import settings

# ── MongoDB client (lazy singleton) ────────────────────────────
_db = None

def _get_db():
    global _db
    if _db is None:
        from pymongo import MongoClient
        client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=8000)
        _db = client[settings.MONGODB_DB]
        # Indexes for fast lookups
        _db["users"].create_index("email", unique=True)
        _db["tokens"].create_index("token", unique=True)
        _db["tokens"].create_index("expires_at", expireAfterSeconds=0)  # TTL index
    return _db


# ── Password helpers ────────────────────────────────────────────
def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return f"{salt}:{hashed.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, hashed_hex = stored.split(":", 1)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(expected.hex(), hashed_hex)
    except Exception:
        return False


# ── Public API ──────────────────────────────────────────────────
def register_user(name: str, email: str, password: str) -> dict:
    """Register a new user. Raises ValueError if email already exists."""
    email = email.lower().strip()
    db = _get_db()

    if db["users"].find_one({"email": email}):
        raise ValueError("An account with this email already exists.")

    db["users"].insert_one({
        "name":          name.strip(),
        "email":         email,
        "password_hash": _hash_password(password),
        "created_at":    time.time(),
    })
    return {"name": name.strip(), "email": email}


def login_user(email: str, password: str) -> dict:
    """Verify credentials. Returns { token, user } on success."""
    email = email.lower().strip()
    db    = _get_db()

    user = db["users"].find_one({"email": email})
    if not user or not _verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password.")

    token = secrets.token_urlsafe(32)
    db["tokens"].insert_one({
        "token":      token,
        "email":      email,
        # Store as datetime for MongoDB TTL index; also keep float for simple check
        "expires_at": time.time() + 30 * 86_400,
    })
    return {
        "token": token,
        "user":  {"name": user["name"], "email": email},
    }


def get_user_from_token(token: str) -> Optional[dict]:
    """Return { name, email } if token is valid and not expired, else None."""
    db    = _get_db()
    entry = db["tokens"].find_one({"token": token})
    if not entry:
        return None
    if time.time() > entry["expires_at"]:
        db["tokens"].delete_one({"token": token})
        return None
    user = db["users"].find_one({"email": entry["email"]})
    if not user:
        return None
    return {"name": user["name"], "email": user["email"]}


def logout_user(token: str) -> None:
    """Delete token from DB (revoke session)."""
    _get_db()["tokens"].delete_one({"token": token})
