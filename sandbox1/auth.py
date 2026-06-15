# sandbox/auth.py
from database import users_db

def verify_user(user_id: str):
    user = users_db.get(user_id)
    if not user:
        raise ValueError("User not found")
    return user