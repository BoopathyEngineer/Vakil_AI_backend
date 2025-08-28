from typing import List

from fastapi.exceptions import HTTPException
from sqlalchemy import insert, select

from app.models.role import Role
from app.models.user_models import User
from app.models.email_models import EmailId
from app.schemas.user_schemas import CreateUser


def get_user_by_username(db, username):
    stmt = select(User).filter(User.username == username)
    result = db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_email(db,email):
    stmt = select(EmailId).filter(EmailId.email_id == email)
    result = db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def create_user(db,user):
    stmt = select(User).filter(User.email == user.email)
    result = db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    stmt = select(User).filter(User.username == user.username)
    result = db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    stmt = insert(User).values(**user.model_dump())
    db.execute(stmt)
    db.commit()

def fetch_user_details(db,email):
    stmt = select(User).filter(User.email == email)
    result = db.execute(stmt)
    user = result.scalars().first()
    return user

def get_user_details(db,filters):
    # fetch user details
    try:
        stmt = select(User).filter_by(**filters)
        result = db.execute(stmt)
        user = result.scalars().first()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")
    
def get_user_info(db,user_id,filters):
    # fetch user details
    try:
        stmt = select(User).filter(User.id != user_id).filter_by(**filters)
        result = db.execute(stmt)
        user = result.scalars().first()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")
    
def get_role_name(db,filters):
    try:
        stmt = select(Role).filter_by(**filters)
        result = db.execute(stmt)
        user = result.scalars().first()
        db.close()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")
    
def get_user_otp(db,email):
    try:
        user = db.query(EmailId).filter(EmailId.email_id == email).first()
        db.close()
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error Occurred")

def fetch_user_email(db,email):
    user = db.query(User).filter(User.email == email).first()
    db.close()
    return user