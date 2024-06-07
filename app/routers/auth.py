from typing import Annotated 
# The Annotated function is used to create a new type hint that combines the original type with additional information or constraints.
from datetime import timedelta

from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    tags=['Authentication']
)

# Login user

@router.post("/login")
def login_users(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()], 
                db: Annotated[Session, Depends(get_db)]):
    # OAuth2PasswordRequestForm is a special class in FastAPI that represents a form for OAuth2 password flow. 
    # It automatically reads the form data(username and password, no email) from the request, validates it, 
    # and makes it available as an instance of OAuth2PasswordRequestForm
    # and injecting it into the user_credentials parameter.
    # When Depends() is used without arguments, it relies on the type hint of the parameter to determine the dependency.
    # FastAPI will automatically detect that OAuth2PasswordRequestForm is a dependency and will handle its creation and injection.
    
     
    # get the user from the users table with the same username in user_credentials
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # if cannot find the user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid Credentials",
            headers={"WWW-Authenticate": "Bearer"}
            ) # you shouldn't tell them what part is wrong
    
    # check if the password is correct
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail=f"Invalid Credentials")
    
    # create a token
    access_token_expires = timedelta(minutes=oauth2.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    # return the token
    return schemas.Token(access_token=access_token, token_type="bearer")