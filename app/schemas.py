from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# user model
class UserBase(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int 
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

# post model

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserResponse # move user schems before this
    
    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None