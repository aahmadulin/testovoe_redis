import json

from fastapi.testclient import TestClient

from app.cache.redis_client import redis_client
from app.db.session import SessionLocal
from app.main import app
from app.models.post import Post


class TestPostCacheIntegration:
    """
    Integration tests for Redis cache logic.
    """

    POSTS_ENDPOINT: str = "/posts"
    CACHE_KEY_PREFIX: str = "post:"
    TEST_TITLE: str = "Cache test title"
    TEST_CONTENT: str = "Cache test content"

    def setup_method(self) -> None:
        """
        Prepare test environment before each test.
        """
        self.client: TestClient = TestClient(app)
        redis_client.flushdb()

    def teardown_method(self) -> None:
        """
        Clean test environment after each test.
        """
        db = SessionLocal()

        try:
            db.query(Post).delete()
            db.commit()
        finally:
            db.close()

        redis_client.flushdb()

    def test_get_post_returns_data_from_cache_after_db_delete(self) -> None:
        """
        Verify that after the first GET request:
        1. post is stored in Redis
        2. if the row is deleted from PostgreSQL
        3. second GET still returns data from Redis cache
        """
        create_response = self.client.post(
            self.POSTS_ENDPOINT,
            json={
                "title": self.TEST_TITLE,
                "content": self.TEST_CONTENT
            }
        )

        assert create_response.status_code == 200

        created_post: dict = create_response.json()
        post_id: int = created_post["id"]
        cache_key: str = f"{self.CACHE_KEY_PREFIX}{post_id}"

        first_get_response = self.client.get(f"{self.POSTS_ENDPOINT}/{post_id}")

        assert first_get_response.status_code == 200
        assert first_get_response.json()["id"] == post_id

        cached_value: str | None = redis_client.get(cache_key)

        assert cached_value is not None

        cached_post: dict = json.loads(cached_value)

        assert cached_post["id"] == post_id
        assert cached_post["title"] == self.TEST_TITLE
        assert cached_post["content"] == self.TEST_CONTENT

        db = SessionLocal()

        try:
            post_in_db: Post | None = db.query(Post).filter(Post.id == post_id).first()

            assert post_in_db is not None

            db.delete(post_in_db)
            db.commit()
        finally:
            db.close()

        second_get_response = self.client.get(f"{self.POSTS_ENDPOINT}/{post_id}")

        assert second_get_response.status_code == 200
        assert second_get_response.json()["id"] == post_id
        assert second_get_response.json()["title"] == self.TEST_TITLE
        assert second_get_response.json()["content"] == self.TEST_CONTENT