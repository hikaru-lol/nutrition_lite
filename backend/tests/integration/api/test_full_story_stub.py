# tests/integration_real/api/test_full_story_stub.py
from __future__ import annotations

import os
import uuid
from datetime import date
from pprint import pformat
from typing import Any

import pytest
from fastapi.testclient import TestClient

# --- OpenAI を絶対に叩かない（env-file を使わなくても Stub になるよう保険） ---
os.environ.setdefault("USE_OPENAI_TARGET_GENERATOR", "false")
os.environ.setdefault("USE_OPENAI_NUTRITION_ESTIMATOR", "false")
os.environ.setdefault("USE_OPENAI_DAILY_REPORT_GENERATOR", "false")

from app.main import create_app  # noqa: E402

pytestmark = pytest.mark.real_integration
DEBUG = os.getenv("E2E_DEBUG") == "1"


def _make_client() -> TestClient:
    return TestClient(create_app())


def _safe_json(resp) -> Any:
    try:
        return resp.json()
    except Exception:
        return None


def _dump_resp(label: str, resp) -> None:
    if not DEBUG:
        return
    req = getattr(resp, "request", None)
    method = getattr(req, "method", "?")
    url = getattr(req, "url", "?")
    print(f"\n=== {label} ===")
    print(f"request: {method} {url}")
    print("status :", resp.status_code)
    js = _safe_json(resp)
    if js is not None:
        print("json   :", pformat(js, width=120))
    else:
        print("text   :", resp.text)


def _assert_status(resp, expected: int, label: str) -> None:
    if resp.status_code != expected:
        req = getattr(resp, "request", None)
        method = getattr(req, "method", "?")
        url = getattr(req, "url", "?")
        js = _safe_json(resp)
        detail = pformat(js, width=120) if js is not None else resp.text
        raise AssertionError(
            f"[{label}] expected {expected}, got {resp.status_code}\n"
            f"request: {method} {url}\n"
            f"response: {detail}"
        )


def _request(client: TestClient, label: str, method: str, url: str, **kwargs):
    resp = client.request(method, url, **kwargs)
    _dump_resp(label, resp)
    return resp


def test_full_story_stub_flow() -> None:
    """
    E2E stub flow:
    register -> profile -> target -> meals -> nutrition -> daily report(create/get)
    """
    client = _make_client()

    # 1) Register
    email = f"e2e_stub_{uuid.uuid4().hex}@example.com"
    password = "RealStoryPass123!"
    name = "E2E Stub User"

    register_resp = _request(
        client,
        "REGISTER",
        "POST",
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    _assert_status(register_resp, 201, "REGISTER")
    user_id = register_resp.json()["user"]["id"]

    # 1.5) Login
    login_resp = _request(
        client,
        "LOGIN",
        "POST",
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    _assert_status(login_resp, 200, "LOGIN")

    # 2) Profile
    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        "meals_per_day": 3,
    }
    profile_put_resp = _request(
        client, "PROFILE PUT", "PUT", "/api/v1/profile/me", json=profile_payload
    )
    _assert_status(profile_put_resp, 200, "PROFILE PUT")

    profile_get_resp = _request(
        client, "PROFILE GET", "GET", "/api/v1/profile/me")
    _assert_status(profile_get_resp, 200, "PROFILE GET")
    profile_get = profile_get_resp.json()
    assert profile_get["user_id"] == user_id
    assert profile_get["meals_per_day"] == 3

    # 3) Target
    target_payload = {
        "title": "E2E Stub Target",
        "goal_type": "weight_loss",
        "goal_description": None,
        "activity_level": "normal",
    }
    target_resp = _request(
        client, "TARGET CREATE", "POST", "/api/v1/targets", json=target_payload
    )
    _assert_status(target_resp, 201, "TARGET CREATE")
    target_data = target_resp.json()
    assert target_data["user_id"] == user_id
    assert target_data["is_active"] is True

    # 4) Meals (main 1..3)
    target_date = date(2025, 1, 2)
    target_date_str = target_date.isoformat()

    for meal_index in (1, 2, 3):
        meal_payload = {
            "date": target_date_str,
            "meal_type": "main",
            "meal_index": meal_index,
            "name": f"Meal {meal_index}",
            "amount_value": 200.0,
            "amount_unit": "g",
            "serving_count": None,
            "note": None,
        }
        meal_resp = _request(
            client,
            f"MEAL CREATE main#{meal_index}",
            "POST",
            "/api/v1/meal-items",
            json=meal_payload,
        )
        _assert_status(meal_resp, 201, f"MEAL CREATE main#{meal_index}")

    # 5) Nutrition generation for each meal
    for meal_index in (1, 2, 3):
        nutrition_resp = _request(
            client,
            f"NUTRITION MEAL main#{meal_index}",
            "GET",
            "/api/v1/nutrition/meal",
            params={
                "date": target_date_str,
                "meal_type": "main",
                "meal_index": meal_index,
            },
        )
        _assert_status(nutrition_resp, 200,
                       f"NUTRITION MEAL main#{meal_index}")
        nutrition_data = nutrition_resp.json()
        assert "meal" in nutrition_data
        assert "daily" in nutrition_data
        assert nutrition_data["meal"]["date"] == target_date_str
        assert nutrition_data["daily"]["date"] == target_date_str
        assert len(nutrition_data["meal"]["nutrients"]) > 0

    # 6) Daily report generation
    report_resp = _request(
        client,
        "DAILY REPORT CREATE",
        "POST",
        "/api/v1/nutrition/daily/report",
        json={"date": target_date_str},
    )
    _assert_status(report_resp, 201, "DAILY REPORT CREATE")
    report_data = report_resp.json()
    assert report_data["date"] == target_date_str
    assert isinstance(report_data["summary"],
                      str) and report_data["summary"].strip()
    assert isinstance(report_data["good_points"],
                      list) and report_data["good_points"]
    assert isinstance(report_data["improvement_points"],
                      list) and report_data["improvement_points"]
    assert isinstance(report_data["tomorrow_focus"],
                      list) and report_data["tomorrow_focus"]

    # 7) Daily report retrieval
    report_get_resp = _request(
        client,
        "DAILY REPORT GET",
        "GET",
        "/api/v1/nutrition/daily/report",
        params={"date": target_date_str},
    )
    _assert_status(report_get_resp, 200, "DAILY REPORT GET")
    report_get = report_get_resp.json()
    assert report_get["date"] == target_date_str
    assert report_get["summary"] == report_data["summary"]
