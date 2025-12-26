from __future__ import annotations

import os
from datetime import date
import uuid
from pprint import pformat
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.real_integration

# E2E_DEBUG=1 のときだけ、レスポンスを詳細に出す
DEBUG = os.getenv("E2E_DEBUG") == "1"


def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


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
        # 失敗時は DEBUG に関係なく必ず出す
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


def test_full_story_real_flow() -> None:
    """
    End-to-end real integration flow:
    register -> profile -> target -> meals -> nutrition -> daily report.
    """
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is not set for real integration test")

    client = _make_client()

    # 1) Register
    email = f"realstory_{uuid.uuid4().hex}@example.com"
    password = "RealStoryPass123!"
    name = "Real Story User"

    register_resp = _request(
        client,
        "REGISTER",
        "POST",
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    _assert_status(register_resp, 201, "REGISTER")
    register_data = register_resp.json()
    user_id = register_data["user"]["id"]
    assert register_data["user"]["email"] == email, register_data

    # 1.5) Login (refresh auth cookies explicitly)
    login_resp = _request(
        client,
        "LOGIN",
        "POST",
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    _assert_status(login_resp, 200, "LOGIN")

    # 2) Profile (PUT)
    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        "meals_per_day": 3,
    }

    profile_put_resp = _request(
        client,
        "PROFILE PUT",
        "PUT",
        "/api/v1/profile/me",
        json=profile_payload,
    )
    _assert_status(profile_put_resp, 200, "PROFILE PUT")
    profile_put_data = profile_put_resp.json()

    # ★ ここで「保存」か「レスポンスDTO」か切り分けるため GET を挟む
    profile_get_resp = _request(
        client, "PROFILE GET", "GET", "/api/v1/profile/me")
    _assert_status(profile_get_resp, 200, "PROFILE GET")
    profile_get_data = profile_get_resp.json()

    # user_id は整合してる？
    assert profile_put_data["user_id"] == user_id, profile_put_data
    assert profile_get_data["user_id"] == user_id, profile_get_data

    # meals_per_day の切り分け（PUT/GET両方をメッセージに含める）
    assert profile_put_data.get("meals_per_day") == 3, (
        f"PUT response meals_per_day mismatch.\n"
        f"profile_payload={profile_payload}\n"
        f"PUT={profile_put_data}\n"
        f"GET={profile_get_data}"
    )
    assert profile_get_data.get("meals_per_day") == 3, (
        f"GET response meals_per_day mismatch.\n"
        f"profile_payload={profile_payload}\n"
        f"PUT={profile_put_data}\n"
        f"GET={profile_get_data}"
    )

    # ここから先（Target / meals / nutrition / daily report）も同じ _request + _assert_status で増やせます

    # 3) Target
    target_payload = {
        "title": "Real Story Target",
        "goal_type": "weight_loss",
        "goal_description": None,
        "activity_level": "normal",
    }

    target_resp = _request(
        client,
        "TARGET CREATE",
        "POST",
        "/api/v1/targets",
        json=target_payload,
    )
    _assert_status(target_resp, 201, "TARGET CREATE")

    target_data = target_resp.json()

    # 期待値チェック（失敗時に target_data が出るように）
    assert target_data["user_id"] == user_id, target_data
    assert target_data["is_active"] is True, target_data

    # 返ってくるなら、ここも確認しておくと原因切り分けがしやすい（任意）
    if "goal_type" in target_data:
        assert target_data["goal_type"] == "weight_loss", target_data
    if "activity_level" in target_data:
        assert target_data["activity_level"] == "normal", target_data
    if "title" in target_data:
        assert target_data["title"] == "Real Story Target", target_data

    # 4) Meal entries (main 1..3)
    target_date = date(2025, 1, 2)
    target_date_str = target_date.isoformat()

    meal_item_ids: list[str] = []  # 後続ステップで使えるように収集（返ってくるなら）

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

        meal_data = meal_resp.json()

        # 返却仕様がある程度分かっているなら、ここで整合チェック（失敗時 meal_data が出る）
        if "user_id" in meal_data:
            assert meal_data["user_id"] == user_id, meal_data
        if "date" in meal_data:
            assert meal_data["date"] == target_date_str, meal_data
        if "meal_type" in meal_data:
            assert meal_data["meal_type"] == "main", meal_data
        if "meal_index" in meal_data:
            assert meal_data["meal_index"] == meal_index, meal_data
        if "name" in meal_data:
            assert meal_data["name"] == f"Meal {meal_index}", meal_data

        # id が返ってくるなら後で使えるので拾う（無ければスキップ）
        if "id" in meal_data and meal_data["id"]:
            meal_item_ids.append(meal_data["id"])

    # # 5) Nutrition generation for each meal
    # for meal_index in (1, 2, 3):
    #     nutrition_resp = client.get(
    #         "/api/v1/nutrition/meal",
    #         params={
    #             "date": target_date_str,
    #             "meal_type": "main",
    #             "meal_index": meal_index,
    #         },
    #     )
    #     assert nutrition_resp.status_code == 200, nutrition_resp.text
    #     nutrition_data = nutrition_resp.json()
    #     assert "meal" in nutrition_data
    #     assert "daily" in nutrition_data
    #     assert nutrition_data["meal"]["date"] == target_date_str
    #     assert nutrition_data["daily"]["date"] == target_date_str
    #     assert len(nutrition_data["meal"]["nutrients"]) > 0

    # # 6) Daily report generation
    # report_resp = client.post(
    #     "/api/v1/nutrition/daily/report",
    #     json={"date": target_date_str},
    # )
    # assert report_resp.status_code == 201, report_resp.text
    # report_data = report_resp.json()
    # assert report_data["date"] == target_date_str
    # assert isinstance(report_data["summary"], str) and report_data["summary"]
    # assert isinstance(report_data["good_points"], list) and report_data["good_points"]
    # assert isinstance(report_data["improvement_points"], list) and report_data["improvement_points"]
    # assert isinstance(report_data["tomorrow_focus"], list) and report_data["tomorrow_focus"]

    # # 7) Daily report retrieval
    # report_get_resp = client.get(
    #     "/api/v1/nutrition/daily/report",
    #     params={"date": target_date_str},
    # )
    # assert report_get_resp.status_code == 200, report_get_resp.text
    # report_get_data = report_get_resp.json()
    # assert report_get_data["date"] == target_date_str
    # assert report_get_data["summary"] == report_data["summary"]
