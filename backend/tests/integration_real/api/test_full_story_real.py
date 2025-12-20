import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


pytestmark = pytest.mark.real_integration


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_full_story_real_flow() -> None:
    """
    End-to-end real integration flow:
    register -> profile -> target -> meals -> nutrition -> daily report.
    """
    client = _make_client()

    # 1) Register
    email = f"realstory_{uuid.uuid4().hex}@example.com"
    password = "RealStoryPass123!"
    name = "Real Story User"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )
    assert register_resp.status_code == 201, register_resp.text

    register_data = register_resp.json()
    assert "user" in register_data
    user_id = register_data["user"]["id"]
    assert register_data["user"]["email"] == email

    # 2) Profile
    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        "meals_per_day": 3,
    }
    profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
    assert profile_resp.status_code == 200, profile_resp.text
    profile_data = profile_resp.json()
    assert profile_data["user_id"] == user_id
    assert profile_data["meals_per_day"] == 3

    # 3) Target
    target_payload = {
        "title": "Real Story Target",
        "goal_type": "weight_loss",
        "goal_description": None,
        "activity_level": "normal",
    }
    target_resp = client.post("/api/v1/targets", json=target_payload)
    assert target_resp.status_code == 201, target_resp.text
    target_data = target_resp.json()
    assert target_data["user_id"] == user_id
    assert target_data["is_active"] is True

    # 4) Meal entries (main 1..3)
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
        meal_resp = client.post("/api/v1/meal-items", json=meal_payload)
        assert meal_resp.status_code == 201, meal_resp.text

    # 5) Nutrition generation for each meal
    for meal_index in (1, 2, 3):
        nutrition_resp = client.get(
            "/api/v1/nutrition/meal",
            params={
                "date": target_date_str,
                "meal_type": "main",
                "meal_index": meal_index,
            },
        )
        assert nutrition_resp.status_code == 200, nutrition_resp.text
        nutrition_data = nutrition_resp.json()
        assert "meal" in nutrition_data
        assert "daily" in nutrition_data
        assert nutrition_data["meal"]["date"] == target_date_str
        assert nutrition_data["daily"]["date"] == target_date_str
        assert len(nutrition_data["meal"]["nutrients"]) > 0

    # 6) Daily report generation
    report_resp = client.post(
        "/api/v1/nutrition/daily/report",
        json={"date": target_date_str},
    )
    assert report_resp.status_code == 201, report_resp.text
    report_data = report_resp.json()
    assert report_data["date"] == target_date_str
    assert isinstance(report_data["summary"], str) and report_data["summary"]
    assert isinstance(report_data["good_points"], list) and report_data["good_points"]
    assert isinstance(report_data["improvement_points"], list) and report_data["improvement_points"]
    assert isinstance(report_data["tomorrow_focus"], list) and report_data["tomorrow_focus"]

    # 7) Daily report retrieval
    report_get_resp = client.get(
        "/api/v1/nutrition/daily/report",
        params={"date": target_date_str},
    )
    assert report_get_resp.status_code == 200, report_get_resp.text
    report_get_data = report_get_resp.json()
    assert report_get_data["date"] == target_date_str
    assert report_get_data["summary"] == report_data["summary"]
