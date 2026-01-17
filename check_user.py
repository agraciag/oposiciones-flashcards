
from backend.database import SessionLocal
from backend.models import User
import sys
import os

# Add backend directory to path so imports work
sys.path.append(os.path.join(os.getcwd(), 'backend'))

def check_user(username):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            print(f"User found: ID={user.id}, Username={user.username}, Email={user.email}")
            print(f"Hashed Password: {user.hashed_password}")
        else:
            print(f"User '{username}' not found.")
    except Exception as e:
        print(f"Error checking user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user("alejandro")
