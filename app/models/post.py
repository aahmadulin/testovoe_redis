from sqlalchemy import Column, DateTime, Index, Integer, String, Text, func

from app.db.base import Base


class Post(Base):
    """
    SQLAlchemy model for blog posts.
    """

    __tablename__ = "posts"

    TITLE_MAX_LENGTH: int = 255

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(TITLE_MAX_LENGTH), nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    __table_args__ = (
        Index("idx_posts_id", "id"),
    )