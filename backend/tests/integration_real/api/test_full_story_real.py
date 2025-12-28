# 　テスト実行時に環境変数の読み込みが必要になるので、.envファイルを読み込む

from __future__ import annotations

import os
import uuid
from datetime import date
from pprint import pformat
from typing import Any, Literal, NotRequired, TypedDict, cast

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.real_integration

# E2E_DEBUG=1 のときだけ、レスポンスを詳細に出す
DEBUG = os.getenv("E2E_DEBUG") == "1"


# =========================
# TypedDicts (API Responses)
# =========================

Plan = Literal["free", "trial", "paid"]
Sex = Literal["male", "female"]
MealTypeStr = Literal["main", "snack"]
NutrientSourceStr = Literal["llm", "stub", "manual"]  # あなたの実装に合わせて調整


class UserJSON(TypedDict):
    id: str
    email: str
    name: str
    plan: Plan
    has_profile: bool
    created_at: str
    trial_ends_at: NotRequired[str]  # paid/freeなら無い可能性があるならNotRequired


class AuthResponseJSON(TypedDict):
    user: UserJSON


class ProfileJSON(TypedDict):
    user_id: str
    sex: Sex
    birthdate: str
    height_cm: float
    weight_kg: float
    meals_per_day: int | None
    image_id: str | None
    created_at: str
    updated_at: str


class TargetNutrientJSON(TypedDict):
    code: str
    amount: float
    unit: str
    source: NutrientSourceStr | str  # 実際の source 文字列に合わせてゆるく


class TargetJSON(TypedDict):
    id: str
    user_id: str
    title: str
    goal_type: str
    goal_description: str | None
    activity_level: str
    is_active: bool
    disclaimer: str
    llm_rationale: str | None
    nutrients: list[TargetNutrientJSON]
    created_at: str
    updated_at: str


class MealItemJSON(TypedDict):
    id: str
    date: str
    meal_type: MealTypeStr | str
    meal_index: int | None
    name: str
    amount_value: float | None
    amount_unit: str | None
    serving_count: float | None
    note: str | None


class MealNutrientJSON(TypedDict):
    code: str
    amount: float
    unit: str
    source: str


class MealNutritionJSON(TypedDict):
    date: str
    meal_type: str
    meal_index: int | None
    nutrients: list[MealNutrientJSON]


class DailyNutritionJSON(TypedDict):
    date: str
    nutrients: list[MealNutrientJSON]


class NutritionResponseJSON(TypedDict):
    meal: MealNutritionJSON
    daily: DailyNutritionJSON


class DailyReportJSON(TypedDict):
    date: str
    summary: str
    good_points: list[str]
    improvement_points: list[str]
    tomorrow_focus: list[str]


# =========================
# Helpers
# =========================

def _make_client() -> TestClient:
    app = create_app()
    return TestClient(app)


def _safe_json(resp: httpx.Response) -> Any | None:
    try:
        return resp.json()
    except Exception:
        return None


def _dump_resp(label: str, resp: httpx.Response) -> None:
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


def _assert_status(resp: httpx.Response, expected: int, label: str) -> None:
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


def _request(
    client: TestClient,
    label: str,
    method: str,
    url: str,
    **kwargs: Any,
) -> httpx.Response:
    resp = client.request(method, url, **kwargs)
    _dump_resp(label, resp)
    return resp


# =========================
# Test
# =========================

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
    register_data = cast(AuthResponseJSON, register_resp.json())

    user_id: str = register_data["user"]["id"]
    assert register_data["user"]["email"] == email, register_data
    assert register_data["user"]["plan"] in (
        "trial", "paid"), register_data  # premiumの前提なら

    # 1.5) Login
    login_resp = _request(
        client,
        "LOGIN",
        "POST",
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    _assert_status(login_resp, 200, "LOGIN")
    login_data = cast(AuthResponseJSON, login_resp.json())
    assert login_data["user"]["id"] == user_id, login_data

    # 2) Profile (PUT + GET)
    profile_payload: dict[str, Any] = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        "meals_per_day": 3,
    }

    profile_put_resp = _request(
        client, "PROFILE PUT", "PUT", "/api/v1/profile/me", json=profile_payload)
    _assert_status(profile_put_resp, 200, "PROFILE PUT")
    profile_put_data = cast(ProfileJSON, profile_put_resp.json())

    profile_get_resp = _request(
        client, "PROFILE GET", "GET", "/api/v1/profile/me")
    _assert_status(profile_get_resp, 200, "PROFILE GET")
    profile_get_data = cast(ProfileJSON, profile_get_resp.json())

    assert profile_put_data["user_id"] == user_id, profile_put_data
    assert profile_get_data["user_id"] == user_id, profile_get_data
    assert profile_put_data["meals_per_day"] == 3, {
        "PUT": profile_put_data, "GET": profile_get_data}
    assert profile_get_data["meals_per_day"] == 3, {
        "PUT": profile_put_data, "GET": profile_get_data}

    # 3) Target
    target_payload: dict[str, Any] = {
        "title": "Real Story Target",
        "goal_type": "weight_loss",
        "goal_description": None,
        "activity_level": "normal",
    }

    target_resp = _request(client, "TARGET CREATE", "POST",
                           "/api/v1/targets", json=target_payload)
    _assert_status(target_resp, 201, "TARGET CREATE")
    target_data = cast(TargetJSON, target_resp.json())

    assert target_data["user_id"] == user_id, target_data
    assert target_data["is_active"] is True, target_data
    assert target_data["goal_type"] == "weight_loss", target_data
    assert target_data["activity_level"] == "normal", target_data
    assert target_data["title"] == "Real Story Target", target_data

    # 4) Meal entries (main 1..3)
    target_date: date = date(2025, 1, 2)
    target_date_str: str = target_date.isoformat()

    meal_item_ids: list[str] = []

    for meal_index in (1, 2, 3):
        meal_payload: dict[str, Any] = {
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
            client, f"MEAL CREATE main#{meal_index}", "POST", "/api/v1/meal-items", json=meal_payload)
        _assert_status(meal_resp, 201, f"MEAL CREATE main#{meal_index}")
        meal_data = cast(MealItemJSON, meal_resp.json())

        assert meal_data["date"] == target_date_str, meal_data
        assert meal_data["meal_type"] == "main", meal_data
        assert meal_data["meal_index"] == meal_index, meal_data
        assert meal_data["name"] == f"Meal {meal_index}", meal_data

        if meal_data.get("id"):
            meal_item_ids.append(meal_data["id"])

    # 5) Nutrition generation for each meal
    for meal_index in (1, 2, 3):
        nutrition_resp = _request(
            client,
            f"NUTRITION MEAL main#{meal_index}",
            "GET",
            "/api/v1/nutrition/meal",
            params={"date": target_date_str,
                    "meal_type": "main", "meal_index": meal_index},
        )
        _assert_status(nutrition_resp, 200,
                       f"NUTRITION MEAL main#{meal_index}")
        nutrition_data = cast(NutritionResponseJSON, nutrition_resp.json())

        assert nutrition_data["meal"]["date"] == target_date_str, nutrition_data
        assert nutrition_data["daily"]["date"] == target_date_str, nutrition_data
        assert len(nutrition_data["meal"]["nutrients"]) > 0, nutrition_data

    # 6) Daily report generation
    report_resp = _request(
        client,
        "DAILY REPORT CREATE",
        "POST",
        "/api/v1/nutrition/daily/report",
        json={"date": target_date_str},
    )
    _assert_status(report_resp, 201, "DAILY REPORT CREATE")
    report_data = cast(DailyReportJSON, report_resp.json())

    assert report_data["date"] == target_date_str, report_data
    assert isinstance(
        report_data["summary"], str) and report_data["summary"].strip(), report_data
    assert isinstance(report_data["good_points"], list) and len(
        report_data["good_points"]) > 0, report_data
    assert isinstance(report_data["improvement_points"], list) and len(
        report_data["improvement_points"]) > 0, report_data
    assert isinstance(report_data["tomorrow_focus"], list) and len(
        report_data["tomorrow_focus"]) > 0, report_data

    # 7) Daily report retrieval
    report_get_resp = _request(
        client,
        "DAILY REPORT GET",
        "GET",
        "/api/v1/nutrition/daily/report",
        params={"date": target_date_str},
    )
    _assert_status(report_get_resp, 200, "DAILY REPORT GET")
    report_get_data = cast(DailyReportJSON, report_get_resp.json())

    assert report_get_data["date"] == target_date_str, report_get_data
    assert report_get_data["summary"] == report_data["summary"], {
        "created": report_data, "fetched": report_get_data}
