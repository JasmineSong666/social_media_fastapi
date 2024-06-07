from passlib.context import CryptContext

# tell passlib to use bcrypt to hash the password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# hash the password
def get_password_hash(password: str):
    return pwd_context.hash(password)

# verify the password
def verify_password(password:str, hashed_password:str):
    return pwd_context.verify(password, hashed_password)