import json
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.cache.redis_client import redis_client
from app.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate


load_dotenv()
logger: logging.Logger = logging.getLogger(__name__)


class PostService:
    """
    Service layer responsible for business logic related to posts.

    Handles interaction between:
    - API layer
    - Repository layer
    - Redis cache
    """

    # вынес в константы для удобства настройки и тестирования
    CACHE_PREFIX: str = "post:"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL"))

    def __init__(self, db: Session) -> None:
        """
        Initialize PostService.

        Args:
            db (Session): SQLAlchemy database session.
        """
        self.db: Session = db

    def _generate_cache_key(self, post_id: int) -> str:
        """
        Generate Redis cache key for a post.

        Args:
            post_id (int): Post identifier.

        Returns:
            str: Redis cache key.
        """
        return f"{self.CACHE_PREFIX}{post_id}"

    def _serialize_post(self, post: Post) -> str:
        """
        Serialize Post object to JSON string for Redis storage.

        Args:
            post (Post): Post model instance.

        Returns:
            str: JSON serialized post.
        """
        post_dict: dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content
        }

        return json.dumps(post_dict)

    def _deserialize_post(self, serialized_post: str) -> Post:
        """
        Deserialize JSON string from Redis into Post object.

        Args:
            serialized_post (str): JSON serialized post.

        Returns:
            Post: Reconstructed Post object.
        """
        data: dict = json.loads(serialized_post)

        return Post(
            id=data["id"],
            title=data["title"],
            content=data["content"]
        )

    def create_post(self, post_data: PostCreate) -> Post:
        """
        Create a new post.

        Args:
            post_data (PostCreate): Input schema.

        Returns:
            Post: Created post instance.
        """
        return PostRepository.create(
            db=self.db,
            title=post_data.title,
            content=post_data.content
        )

    def get_post(self, post_id: int) -> Optional[Post]:
        """
        Retrieve post using cache-first strategy.

        Steps:
        1. Check Redis cache
        2. If miss → fetch from database
        3. Save result to Redis
        """

        cache_key: str = self._generate_cache_key(post_id)

        cached_post: Optional[str] = None

        try:
            cached_post = redis_client.get(cache_key)

        except Exception as redis_error:
            logger.error(
                "Redis read error",
                extra={"post_id": post_id, "error": str(redis_error)}
            )

        if cached_post is not None:
            logger.info(
                "Cache hit",
                extra={"post_id": post_id}
            )

            return self._deserialize_post(cached_post)

        logger.info(
            "Cache miss",
            extra={"post_id": post_id}
        )

        post: Optional[Post] = PostRepository.get(self.db, post_id)

        if post is None:
            return None

        try:
            redis_client.setex(
                cache_key,
                self.CACHE_TTL,
                self._serialize_post(post)
            )

        except Exception as redis_error:
            logger.error(
                "Redis write error",
                extra={"post_id": post_id, "error": str(redis_error)}
            )

        return post

    def update_post(self, post_id: int, post_data: PostUpdate) -> Optional[Post]:
        """
        Update post and invalidate cache.
        """

        post: Optional[Post] = PostRepository.get(self.db, post_id)

        if post is None:
            return None

        updated_post: Post = PostRepository.update(
            db=self.db,
            post=post,
            title=post_data.title,
            content=post_data.content
        )

        cache_key: str = self._generate_cache_key(post_id)

        try:
            redis_client.delete(cache_key)

        except Exception as redis_error:
            logger.error(
                "Redis cache invalidation error",
                extra={"post_id": post_id, "error": str(redis_error)}
            )

        return updated_post

    def delete_post(self, post_id: int) -> bool:
        """
        Delete post and invalidate cache.
        """

        post: Optional[Post] = PostRepository.get(self.db, post_id)

        if post is None:
            return False

        PostRepository.delete(self.db, post)

        cache_key: str = self._generate_cache_key(post_id)

        try:
            redis_client.delete(cache_key)

        except Exception as redis_error:
            logger.error(
                "Redis cache invalidation error",
                extra={"post_id": post_id, "error": str(redis_error)}
            )

        return True