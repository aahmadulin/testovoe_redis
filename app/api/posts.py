from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.post import PostCreate, PostUpdate, PostResponse
from app.services.post_service import PostService


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse)
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)) -> PostResponse:
    """
    Create a new blog post.
    """
    service: PostService = PostService(db)

    post = service.create_post(post_data)

    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Session = Depends(get_db)) -> PostResponse:
    """
    Retrieve a post by ID with Redis caching.
    """
    service: PostService = PostService(db)

    post = service.get_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db)) -> PostResponse:
    """
    Update a blog post.
    """
    service: PostService = PostService(db)

    post = service.update_post(post_id, post_data)

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.delete("/{post_id}")
async def delete_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Delete a blog post.
    """
    service: PostService = PostService(db)

    deleted: bool = service.delete_post(post_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"message": "Post deleted"}