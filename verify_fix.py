
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.auth_utils import verify_password, get_password_hash

try:
    password = "testpassword"
    hashed = get_password_hash(password)
    print(f"Hash generated: {hashed}")
    
    result = verify_password(password, hashed)
    print(f"Verification result: {result}")
except Exception as e:
    print(f"Error: {e}")
