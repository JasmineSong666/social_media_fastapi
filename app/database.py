from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
# from pydantic import BaseModel
# import psycopg
# import time

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
# postgresql://<username>:<password>@<server/hostname>/<database_name>

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# The yield keyword in Python is used to create a context manager. When a route that depends on this get_db() function is called, the yield statement returns the database session. 
# This session is then used within the route's function to interact with the database.


# use PostgreSQL driver — Psycopg to connect to the database, but we don't need this anymore we have SqlAlchemy
# # connect to database
# # keep trying to connect until it succeeds

# while True:
#     try: 
#         # Connect to an existing database
#         conn = psycopg.connect(
#             host='localhost', 
#             dbname='FASTAPI_SOCIAL_MEDIA', 
#             user='postgres', 
#             password='903666', 
#             row_factory=dict_row   # By default, a cursor in Psycopg returns query results as tuples. If you want your query results to be returned as dictionaries where column names are the keys, you should use dict_row for dictionary-like rows
#         )
#         # Open a cursor to perform database operations
#         cur = conn.cursor() 
#         print("Successfully connected to the database")
#         break  # Exit the loop if the connection is successful
#     except Exception as error:
#         print("Error connecting to database")
#         print(f"Error: {error}")
#         time.sleep(2) # wait for 2 seconds before trying again
#     # finally:
#     #     # Clean up resources if they were allocated
#     #     try:
#     #         if cur:
#     #             cur.close()
#     #     except NameError:
#     #         pass  # cur was not defined, so do nothing
#     #     try:
#     #         if conn:
#     #             conn.close()
#     #     except NameError:
#     #         pass  # conn was not defined, so do nothing
