import logging
from sqlalchemy.orm import Session
from app.models.post import Post

logger: logging.Logger = logging.getLogger(__name__)


class PostRepository:
    """
    Repository layer for database operations related to posts.
    """

    @staticmethod
    def create(db: Session, title: str, content: str) -> Post:
        """
        Create a new post in the database.
        """

        post: Post = Post(title=title, content=content)

        try:
            db.add(post)
            db.commit()
            db.refresh(post)

        except Exception as db_error:
            db.rollback()

            logger.error(
                "Database error during post creation",
                extra={"title": title, "error": str(db_error)}
            )

            raise

        return post

    @staticmethod
    def get(db: Session, post_id: int) -> Post | None:
        """
        Retrieve a post by ID.
        """

        try:
            return db.query(Post).filter(Post.id == post_id).first()

        except Exception as db_error:
            logger.error(
                "Database error during post retrieval",
                extra={"post_id": post_id, "error": str(db_error)}
            )

            raise

    @staticmethod
    def update(
        db: Session,
        post: Post,
        title: str | None,
        content: str | None
    ) -> Post:
        """
        Update an existing post.
        """

        if title is not None:
            post.title = title

        if content is not None:
            post.content = content

        try:
            db.commit()
            db.refresh(post)

        except Exception as db_error:
            db.rollback()

            logger.error(
                "Database error during post update",
                extra={"post_id": post.id, "error": str(db_error)}
            )

            raise

        return post

    @staticmethod
    def delete(db: Session, post: Post) -> None:
        """
        Delete a post from the database.
        """

        try:
            db.delete(post)
            db.commit()

        except Exception as db_error:
            db.rollback()

            logger.error(
                "Database error during post deletion",
                extra={"post_id": post.id, "error": str(db_error)}
            )

            raise