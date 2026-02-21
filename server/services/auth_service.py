from typing import Optional
from sqlalchemy.orm import Session
from models.user import User
from core.security import hash_password, verify_password, create_access_token


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Return a user by username, or None if not found."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, username: str, password: str) -> Optional[User]:
    """Create a new user. Returns the new user or None if username exists."""
    existing_user = get_user_by_username(db, username)
    if existing_user:
        return None

    hashed_password = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(db: Session, username: str, password: str) -> Optional[str]:
    """Verify credentials and return an access token on success.

    If the stored password uses a deprecated scheme (bcrypt) an upgraded
    Argon2 hash will be returned by `verify_password` and persisted.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None

    verified, upgraded_hash = verify_password(password, user.hashed_password)
    if not verified:
        return None

    if upgraded_hash:
        user.hashed_password = upgraded_hash
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.username})
    return token