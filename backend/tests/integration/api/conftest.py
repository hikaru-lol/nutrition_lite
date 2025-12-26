from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


# import 前に env を固定（重要）
os.environ.setdefault("USE_OPENAI_TARGET_GENERATOR", "false")
os.environ.setdefault("USE_OPENAI_NUTRITION_ESTIMATOR", "false")
os.environ.setdefault("USE_OPENAI_DAILY_REPORT_GENERATOR", "false")
os.environ.setdefault("USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR", "false")


def _make_email(prefix: str = "stub") -> str:
    return f"{prefix}_{uuid4().hex}@example.com"


@pytest.fixture(scope="function")
def client() -> TestClient:
    # ここで import することで「env固定 → DI構築」の順になる
    from app.main import create_app

    app = create_app()
    return TestClient(app)


@pytest.fixture(scope="function")
def authed_client(client: TestClient) -> tuple[TestClient, str, str, str]:
    """
    (client, user_id, email, password)
    client には Cookie が入った状態で返る。
    """
    email = _make_email("user")
    password = "Passw0rd!123"
    name = "Stub User"

    r = client.post("/api/v1/auth/register",
                    json={"email": email, "password": password, "name": name})
    assert r.status_code == 201, r.text
    user_id = r.json()["user"]["id"]

    r = client.post("/api/v1/auth/login",
                    json={"email": email, "password": password})
    assert r.status_code == 200, r.text

    return client, user_id, email, password
