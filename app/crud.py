from sqlalchemy.orm import Session
from .models import User, Request


def get_or_create_user(db: Session, user_tg_id: int) -> User:
    user = db.query(User).filter(User.tg_id == user_tg_id).first()

    if not user:
        new_user = User(tg_id=user_tg_id, balance=0)
        db.add(new_user)
        db.commit()
        return user

    return user


def get_users(db: Session) -> list[User]:
    return db.query(User).all()


def create_request(db: Session, state_data: dict, user_tg_id: int) -> User:
    request = Request(
        **state_data, owner_id=get_or_create_user(db, user_tg_id).id)
    db.add(request)
    db.commit()
    return request


def get_requests(db: Session) -> list[Request]:
    return db.query(Request).all()


def increment_balance(db: Session, user_tg_id: int, amount: int):
    user = db.query(User).filter(User.tg_id == user_tg_id).first()
    user.balance = user.balance + amount
    db.commit()


def get_balance(db: Session, user_tg_id: int) -> int:
    return db.query(User).filter(User.tg_id == user_tg_id).first().balance
