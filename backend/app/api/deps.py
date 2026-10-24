from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == "local").first()
    if not user:
        user = User(email="local", password_hash="")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
