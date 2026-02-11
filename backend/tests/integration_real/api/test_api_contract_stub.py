from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta, timezone
from pprint import pformat
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

# ★ OpenAI を絶対に叩かない（env-fileでも設定するが保険）
os.environ.setdefault("USE_OPENAI_TARGET_GENERATOR", "false")
os.environ.setdefault("USE_OPENAI_NUTRITION_ESTIMATOR", "false")
os.environ.setdefault("USE_OPENAI_DAILY_REPORT_GENERATOR", "false")
os.environ.setdefault("USE_OPENAI_MEAL_RECOMMENDATION_GENERATOR", "false")

from app.main import create_app  # noqa: E402
from app.infra.db.session import create_session  # noqa: E402

pytestmark = pytest.mark.real_integration
DEBUG = os.getenv("E2E_DEBUG") == "1"


# -------------------------
# helpers
# -------------------------
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


def _request(client: TestClient, label: str, method: str, url: str, **kwargs):
    resp = client.request(method, url, **kwargs)
    _dump_resp(label, resp)
    return resp


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


def _assert_error(resp, expected_status: int, expected_code: str, label: str) -> None:
    _assert_status(resp, expected_status, label)
    data = resp.json()
    assert "error" in data, data
    assert data["error"]["code"] == expected_code, data


def _register_and_login(client: TestClient) -> dict[str, str]:
    email = f"stub_{uuid.uuid4().hex}@example.com"
    password = "StubPass123!"
    name = "Stub User"

    r = _request(
        client,
        "REGISTER",
        "POST",
        "/api/v1/auth/register",
        json={"email": email, "password": password, "name": name},
    )
    _assert_status(r, 201, "REGISTER")
    user_id = r.json()["user"]["id"]

    l = _request(
        client,
        "LOGIN",
        "POST",
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    _assert_status(l, 200, "LOGIN")

    return {"user_id": user_id, "email": email, "password": password}


def _put_profile(client: TestClient, meals_per_day: int = 3) -> dict[str, Any]:
    payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        "meals_per_day": meals_per_day,
    }
    r = _request(client, "PROFILE PUT", "PUT",
                 "/api/v1/profile/me", json=payload)
    _assert_status(r, 200, "PROFILE PUT")
    return r.json()


def _create_target(client: TestClient, title: str = "Stub Target") -> dict[str, Any]:
    payload = {
        "title": title,
        "goal_type": "weight_loss",
        "goal_description": None,
        "activity_level": "normal",
    }
    r = _request(client, "TARGET CREATE", "POST",
                 "/api/v1/targets", json=payload)
    _assert_status(r, 201, "TARGET CREATE")
    return r.json()


def _create_meal_item(
    client: TestClient,
    target_date: str,
    meal_type: str,
    meal_index: int | None,
    name: str,
    amount_value: float | None = 200.0,
    amount_unit: str | None = "g",
    serving_count: int | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    payload = {
        "date": target_date,
        "meal_type": meal_type,
        "meal_index": meal_index,
        "name": name,
        "amount_value": amount_value,
        "amount_unit": amount_unit,
        "serving_count": serving_count,
        "note": note,
    }
    r = _request(client, f"MEAL CREATE {meal_type}#{meal_index}",
                 "POST", "/api/v1/meal-items", json=payload)
    _assert_status(r, 201, f"MEAL CREATE {meal_type}#{meal_index}")
    return r.json()


def _force_user_free_plan_and_expired_trial(user_id: str) -> None:
    """PlanChecker を確実に落とすため: plan=free + trial_ends_at を過去にする"""
    session = create_session()
    try:
        expired = datetime.now(timezone.utc) - timedelta(days=1)
        session.execute(
            text("UPDATE users SET plan=:plan, trial_ends_at=:trial_ends_at WHERE id=:id"),
            {"plan": "free", "trial_ends_at": expired, "id": user_id},
        )
        session.commit()
    finally:
        session.close()


# -------------------------
# tests
# -------------------------
def test_auth_contract_happy_and_errors() -> None:
    client = _make_client()

    # validation error (bad email)
    bad = _request(
        client,
        "REGISTER bad email",
        "POST",
        "/api/v1/auth/register",
        json={"email": "not-an-email", "password": "12345678", "name": "x"},
    )
    _assert_error(bad, 400, "VALIDATION_ERROR", "REGISTER bad email")

    # register + login
    u = _register_and_login(client)

    # me ok
    me = _request(client, "ME", "GET", "/api/v1/auth/me")
    _assert_status(me, 200, "ME")
    assert me.json()["user"]["id"] == u["user_id"]

    # refresh ok
    ref = _request(client, "REFRESH", "POST", "/api/v1/auth/refresh")
    _assert_status(ref, 200, "REFRESH")
    assert ref.json().get("ok") is True

    # logout -> cookie cleared -> me should be 401 INVALID_ACCESS_TOKEN（実挙動に合わせる）
    lo = _request(client, "LOGOUT", "POST", "/api/v1/auth/logout")
    _assert_status(lo, 204, "LOGOUT")

    me2 = _request(client, "ME after logout", "GET", "/api/v1/auth/me")
    _assert_error(me2, 401, "INVALID_ACCESS_TOKEN", "ME after logout")

    # refresh without cookie -> 401 UNAUTHORIZED
    ref2 = _request(client, "REFRESH no cookie",
                    "POST", "/api/v1/auth/refresh")
    _assert_error(ref2, 401, "UNAUTHORIZED", "REFRESH no cookie")

    # duplicate email -> 409 EMAIL_ALREADY_IN_USE
    c2 = _make_client()
    email = f"dup_{uuid.uuid4().hex}@example.com"
    pw = "DupPass123!"
    r1 = _request(c2, "REGISTER #1", "POST", "/api/v1/auth/register",
                  json={"email": email, "password": pw, "name": "dup"})
    _assert_status(r1, 201, "REGISTER #1")
    r2 = _request(c2, "REGISTER #2", "POST", "/api/v1/auth/register",
                  json={"email": email, "password": pw, "name": "dup"})
    _assert_error(r2, 409, "EMAIL_ALREADY_IN_USE", "REGISTER #2")

    # login invalid credentials -> 401 INVALID_CREDENTIALS
    li = _request(c2, "LOGIN wrong pw", "POST", "/api/v1/auth/login",
                  json={"email": email, "password": "wrong"})
    _assert_error(li, 401, "INVALID_CREDENTIALS", "LOGIN wrong pw")


def test_profile_contract() -> None:
    client = _make_client()
    _register_and_login(client)

    # profile GET before PUT -> 401 USER_NOT_FOUND（現挙動）
    g0 = _request(client, "PROFILE GET before", "GET", "/api/v1/profile/me")
    _assert_error(g0, 404, "PROFILE_NOT_FOUND", "PROFILE GET before")

    # PUT -> GET
    put = _put_profile(client, meals_per_day=3)
    assert put["meals_per_day"] == 3

    g1 = _request(client, "PROFILE GET after", "GET", "/api/v1/profile/me")
    _assert_status(g1, 200, "PROFILE GET after")
    assert g1.json()["meals_per_day"] == 3

    # validation error
    bad = _request(client, "PROFILE PUT bad", "PUT",
                   "/api/v1/profile/me", json={"birthdate": "1990-01-02"})
    _assert_error(bad, 400, "VALIDATION_ERROR", "PROFILE PUT bad")


def test_target_contract_methods_and_errors() -> None:
    client = _make_client()
    _register_and_login(client)

    # profile無しで target create -> 401 USER_NOT_FOUND（現挙動）
    t0 = _request(
        client,
        "TARGET create without profile",
        "POST",
        "/api/v1/targets",
        json={"title": "x", "goal_type": "weight_loss",
              "goal_description": None, "activity_level": "normal"},
    )
    _assert_error(t0, 404, "TARGET_PROFILE_NOT_FOUND",
                  "TARGET create without profile")

    _put_profile(client, meals_per_day=3)

    # create 1st (active)
    t1 = _create_target(client, title="Target 1")
    target_id_1 = t1["id"]
    assert t1["is_active"] is True

    # list (TargetListResponse: {items: [...]})
    lst = _request(client, "TARGET list", "GET", "/api/v1/targets")
    _assert_status(lst, 200, "TARGET list")
    lst_body = lst.json()
    assert "items" in lst_body and isinstance(
        lst_body["items"], list), lst_body
    assert any(x["id"] == target_id_1 for x in lst_body["items"]), lst_body

    # active
    act = _request(client, "TARGET active", "GET", "/api/v1/targets/active")
    _assert_status(act, 200, "TARGET active")
    assert act.json()["id"] == target_id_1

    # get by id
    g1 = _request(client, "TARGET get", "GET",
                  f"/api/v1/targets/{target_id_1}")
    _assert_status(g1, 200, "TARGET get")
    assert g1.json()["id"] == target_id_1

    # patch title
    p1 = _request(client, "TARGET patch", "PATCH",
                  f"/api/v1/targets/{target_id_1}", json={"title": "Target 1 updated"})
    _assert_status(p1, 200, "TARGET patch")
    assert p1.json()["title"] == "Target 1 updated"

    # create 2nd (inactive)
    t2 = _create_target(client, title="Target 2")
    target_id_2 = t2["id"]
    assert t2["is_active"] is False

    # activate 2nd
    a2 = _request(client, "TARGET activate 2", "POST",
                  f"/api/v1/targets/{target_id_2}/activate")
    _assert_status(a2, 200, "TARGET activate 2")
    assert a2.json()["id"] == target_id_2
    assert a2.json()["is_active"] is True

    # /targets/active should return 2nd now
    act2 = _request(client, "TARGET active after activate",
                    "GET", "/api/v1/targets/active")
    _assert_status(act2, 200, "TARGET active after activate")
    assert act2.json()["id"] == target_id_2

    # limit exceeded (max=5) -> 409 TARGET_LIMIT_EXCEEDED
    # already have 2; create 3 more (total 5)
    for i in range(3, 6):
        _create_target(client, title=f"Target {i}")

    too_many = _request(
        client,
        "TARGET limit exceeded",
        "POST",
        "/api/v1/targets",
        json={"title": "Target 6", "goal_type": "weight_loss",
              "goal_description": None, "activity_level": "normal"},
    )
    _assert_error(too_many, 409, "TARGET_LIMIT_EXCEEDED",
                  "TARGET limit exceeded")


def test_meal_contract_methods_and_errors() -> None:
    client = _make_client()
    _register_and_login(client)
    _put_profile(client, meals_per_day=3)

    d = date(2025, 1, 2).isoformat()

    # create
    created = _create_meal_item(client, d, "main", 1, "Meal 1")
    meal_id = created["id"]

    # list (MealItemListResponse: {items: [...]})
    lst = _request(client, "MEAL list", "GET",
                   "/api/v1/meal-items", params={"date": d})
    _assert_status(lst, 200, "MEAL list")
    body = lst.json()
    assert "items" in body and isinstance(body["items"], list), body
    assert any(x["id"] == meal_id for x in body["items"]), body

    # patch (このAPIは「部分更新」ではなく、現状フルボディ想定)
    patch_payload = {
        "date": d,
        "meal_type": "main",
        "meal_index": 1,
        "name": "Meal 1 updated",
        "amount_value": 200.0,
        "amount_unit": "g",
        "serving_count": None,
        "note": None,
    }
    upd = _request(client, "MEAL patch", "PATCH",
                   f"/api/v1/meal-items/{meal_id}", json=patch_payload)
    _assert_status(upd, 200, "MEAL patch")
    assert upd.json()["name"] == "Meal 1 updated"

    # delete
    dele = _request(client, "MEAL delete", "DELETE",
                    f"/api/v1/meal-items/{meal_id}")
    _assert_status(dele, 204, "MEAL delete")

    # not found (patch) -> 404 FOOD_ENTRY_NOT_FOUND（※バリデーションを通すためにフルボディで）
    nf = _request(
        client,
        "MEAL patch notfound",
        "PATCH",
        "/api/v1/meal-items/00000000-0000-0000-0000-000000000000",
        json=patch_payload,
    )
    _assert_error(nf, 404, "FOOD_ENTRY_NOT_FOUND", "MEAL patch notfound")

    # invalid meal_index for main (None) -> 400 INVALID_MEAL_INDEX
    bad_index = _request(
        client,
        "MEAL invalid index",
        "POST",
        "/api/v1/meal-items",
        json={
            "date": d,
            "meal_type": "main",
            "meal_index": None,
            "name": "bad",
            "amount_value": 100,
            "amount_unit": "g",
            "serving_count": None,
            "note": None,
        },
    )
    _assert_error(bad_index, 400, "INVALID_MEAL_INDEX", "MEAL invalid index")

    # invalid food amount -> 400 INVALID_FOOD_AMOUNT
    bad_amt = _request(
        client,
        "MEAL invalid amount",
        "POST",
        "/api/v1/meal-items",
        json={
            "date": d,
            "meal_type": "main",
            "meal_index": 2,
            "name": "bad",
            "amount_value": None,
            "amount_unit": None,
            "serving_count": None,
            "note": None,
        },
    )
    _assert_error(bad_amt, 400, "INVALID_FOOD_AMOUNT", "MEAL invalid amount")
    # --- normal user (trial) ---
