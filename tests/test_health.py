import importlib.util

import pytest

FASTAPI_INSTALLED = importlib.util.find_spec("fastapi") is not None

pytestmark = pytest.mark.skipif(not FASTAPI_INSTALLED, reason="fastapi is not installed")

if FASTAPI_INSTALLED:
    from fastapi.testclient import TestClient

    from api.app import app


    def test_health() -> None:
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
