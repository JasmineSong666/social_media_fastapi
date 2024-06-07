from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import Annotated
router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# create a new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_users(user: schemas.UserCreate, 
                 db: Annotated[Session, Depends(get_db)]):
    
    # hash the password - user.password
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# get user's info
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, 
             db: Annotated[Session, Depends(get_db)], 
             current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {user_id} not found")
    
    return user
