from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from schemas import CRUDException
import secrets

# Generate a secure secret key
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing with Argon2
ph = PasswordHasher()

class AuthHandler:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        try:
            result = ph.verify(hashed_password, plain_password)
            return result
        except VerifyMismatchError:
            return False
        except InvalidHashError:
            return False
        except Exception as e:
            print(f"❌ Password verification error: {e}")
            return False

    @staticmethod
    def get_password_hash(password):
        try:
            return ph.hash(password)
        except Exception as e:
            print(f"❌ Error hashing password: {e}")
            raise CRUDException(f"Error hashing password: {e}", 500)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            to_encode.update({"exp": expire})
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            print(f"❌ Error creating access token: {e}")
            raise CRUDException(f"Error creating token: {e}", 500)

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
        except Exception as e:
            print(f"❌ Error verifying token: {e}")
            return None