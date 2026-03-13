from pwdlib import PasswordHash
from jose import jwt,JWTError
from datetime import datetime, timedelta

from app.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS

password_hash=PasswordHash.recommended()



def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password, hashed):
    try:
        return password_hash.verify(password, hashed)
    except Exception:
        return False

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token

def decode_access_token(token: str):

    try:

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")

        return user_id

    except JWTError:

        return None
def create_refresh_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })

    token = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token 
def decode_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        return None
def decode_refresh_token(token: str):

    payload = decode_token(token)

    if not payload:
        return None

    if payload.get("type") != "refresh":
        return None

    return payload.get("sub")