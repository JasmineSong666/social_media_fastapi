# Social Media FastAPI

## Description

This project is a Social Media API built using FastAPI in Python. 

## Features

- FastAPI for building APIs
- Pydantic for schema validation
- PostgreSQL for database management
- SQLAlchemy ORM for database operations
- JWT for authentication
- pytest for testing
- GitHub Actions for CI/CD

## Install Dependencies
`pip install -r requirements.txt`

## Running the Server
`uvicorn app.main:app --reload`

## API Endpoints
- Users
  - POST /users/ : Create a new user
  - GET /users/{id} : Retrieve a user by ID
- Authentication
  - POST /login/ : Authenticate and receive a token
- Posts
  - CRUD operations for posts
