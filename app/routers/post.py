from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List,  Annotated, Optional
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# get all posts
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)], 
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""):
    # cur.execute("SELECT * FROM posts")
    # posts = cur.fetchall()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts # automatically changed it to JSON, so that we can send over to api

# get the current user's posts
@router.get("/my_posts", response_model=List[schemas.PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)], 
              current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]):
    # cur.execute("SELECT * FROM posts")
    # posts = cur.fetchall()
    posts = db.query(models.Post).filter(models.Post.user_id==current_user.id).all()
    return posts # automatically changed it to JSON, so that we can send over to api

# create a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, 
                 db: Annotated[Session, Depends(get_db)], 
                 current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]): # automatically check if the post from user is conform to Post schema
                            # post is an instance of the Post class = object 
                            # print(post): title='shanghai' content='beijing' published=True rating=4
    # cur.execute("""
    #     INSERT INTO posts (title, content, published)
    #              VALUES (%s, %s, %s)
    #              Returning *  
    #     """,
    #     (post.title, post.content, post.published)) # to prevent SQL injection
    #     # have to add Returning * to get the new post
    # new_post = cur.fetchone()
    # # Make the changes to the database persistent
    # conn.commit()

    # new_post = models.Post(
    #     title=post.title,
    #     content=post.content,
    #     published=post.published,
    # ) # only have the three fields
    # an easy way
    new_post = models.Post(user_id=current_user.id, **post.model_dump()) # add the logged in user id to the new post
    db.add(new_post) # add the new post to the database
    db.commit() # commit the new post
    db.refresh(new_post) # refresh the new_post to get the id and created_at
    return new_post

# get a specific post

@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]): # fastapi would validate if the post_id is an integer
    # cur.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    # post = cur.fetchone()
    post = db.query(models.Post).filter(models.Post.id == post_id).first() # if not include first, it would return a SQL query
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {post_id} not found")
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": "post not found", "id": post_id}
        # add t his before : get_post(post_id: int, response: Response):
    return post
# FastAPI matches the URL pattern and identifies the post_id as a dynamic parameter.
# FastAPI then passes the value of post_id as an argument to the get_post function.

# Delete a specific post

@router.delete("/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]):
    # find the index of the post which has the same id as post_id
    # my_posts.pop(index)
    # cur.execute("DELETE FROM posts WHERE id = %s RETURNING *", (post_id,))
    # deleted_post = cur.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == post_id) # it's not a post, it's a SQL query
    post = post_query.first()

    # if cannot find the index
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {post_id} not found")
    
    # verify id the loggedin user is the owner of the post
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform this action")

    post_query.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    # return {"message": "post was deleted"} 
    # this would generate error since 204 requires response no content.
    # when 204 we don't need to send anything back

# Update a specific post

@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(post_id: int, 
                updated_post: schemas.PostUpdate, 
                db: Annotated[Session, Depends(get_db)], 
                current_user: Annotated[schemas.UserResponse, Depends(oauth2.get_current_user)]):
    # find the index of the post which has the same id as post_id
    # update the post
    # cur.execute("""UPDATE posts 
    #             SET title = %s, content =%s, published =%s
    #             WHERE id = %s RETURNING * """,
    #             (post.title, post.content, post.published, post_id)
    #     )
    # updated_post = cur.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    # if cannot find the index
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {post_id} not found")
    
    # verify id the loggedin user is the owner of the post
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Not authorized to perform this action")
    
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    # post.update({'title': post.title, 'content': post.content})
    db.commit()

    return post_query.first()

