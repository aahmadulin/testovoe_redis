from unittest.mock import MagicMock
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate
from app.services.post_service import PostService

import json


class TestPostService:
    """
    Unit tests for PostService business logic.
    """

    TEST_POST_ID: int = 1
    TEST_TITLE: str = "Test title"
    TEST_CONTENT: str = "Test content"

    def setup_method(self) -> None:
        """
        Prepare mocks for each test.
        """
        self.db: Session = MagicMock()
        self.service: PostService = PostService(self.db)

    def test_generate_cache_key(self) -> None:
        """
        Ensure cache key is generated correctly.
        """
        cache_key: str = self.service._generate_cache_key(self.TEST_POST_ID)

        assert cache_key == f"{self.service.CACHE_PREFIX}{self.TEST_POST_ID}"

    def test_create_post_returns_post_object(self) -> None:
        """
        Ensure create_post returns a Post instance.
        """
        post_data: PostCreate = PostCreate(
            title=self.TEST_TITLE,
            content=self.TEST_CONTENT
        )

        created_post: Post = Post(
            id=self.TEST_POST_ID,
            title=self.TEST_TITLE,
            content=self.TEST_CONTENT
        )

        from app.repositories.post_repository import PostRepository

        PostRepository.create = MagicMock(return_value=created_post)

        result: Post = self.service.create_post(post_data)

        assert result.id == self.TEST_POST_ID
        assert result.title == self.TEST_TITLE
        assert result.content == self.TEST_CONTENT

    def test_get_post_returns_cached_value(self) -> None:
        """
        Ensure cached value is returned without querying DB.
        """

        cached_post = {
            "id": self.TEST_POST_ID,
            "title": self.TEST_TITLE,
            "content": self.TEST_CONTENT
        }

        with patch("app.services.post_service.redis_client.get") as mock_get:
            mock_get.return_value = json.dumps(cached_post)

            result = self.service.get_post(self.TEST_POST_ID)

            assert result is not None
            assert result.id == self.TEST_POST_ID
            assert result.title == self.TEST_TITLE
            assert result.content == self.TEST_CONTENT