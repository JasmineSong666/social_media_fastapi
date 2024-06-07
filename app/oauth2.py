import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from . import schemas, models
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .config import settings
from typing import Annotated 
from datetime import datetime, timedelta, timezone

# get 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

# openssl rand -hex 32
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# create an access token
def create_access_token(data: dict, expires_delta: timedelta | None = None): # data is the payload of the token
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # add the expiry time to the payload
    to_encode.update({"exp": expire}) 
    # encode the payload with the secret key
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# encode token and return the payload data
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    
    return token_data

# get current user based on the token
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]):
    # When you define oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") and use it as a dependency in your route handler, FastAPI will perform the following steps:
    # Extract the Token: FastAPI will look for the Authorization header in the incoming HTTP request. (The extraction of the token by oauth2_scheme in FastAPI is not limited to a specific URL; it applies to any incoming HTTP request that includes the Authorization header with the format Bearer <token>.When you define oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login"), it sets up the expectation that clients will use this URL (/login) to obtain a token. However, this is primarily for the client's knowledge and doesn't restrict the token usage to requests to this URL only.)
    # Validate the Header Format: FastAPI expects the header to be in the format Authorization: Bearer <token>.
    # Retrieve the Token: If the header is present and correctly formatted, FastAPI will extract the token part from the header and pass it to the dependency.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token.id).first()
    
    if user is None:
        raise credentials_exception
    
    return schemas.UserResponse.model_validate(user)
     

    



# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user