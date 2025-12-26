from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta, timezone
from pprint import pformat
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import create_app
from app.infra.db.session import create_session

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

    # cookie refresh（明示的にログインも通しておく）
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
    """
    PlanChecker を確実に落とすため:
    - plan=free
    - trial_ends_at を過去にする
    """
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

    # logout -> cookie cleared -> me should be 401
    lo = _request(client, "LOGOUT", "POST", "/api/v1/auth/logout")
    _assert_status(lo, 204, "LOGOUT")

    me2 = _request(client, "ME after logout", "GET", "/api/v1/auth/me")
    _assert_error(me2, 401, "INVALID_CREDENTIALS", "ME after logout")

    # refresh without cookie -> 401 UNAUTHORIZED
    ref2 = _request(client, "REFRESH no cookie",
                    "POST", "/api/v1/auth/refresh")
    _assert_error(ref2, 401, "UNAUTHORIZED", "REFRESH no cookie")

    # duplicate email -> 409
    c2 = _make_client()
    email = f"dup_{uuid.uuid4().hex}@example.com"
    pw = "DupPass123!"
    r1 = _request(c2, "REGISTER #1", "POST", "/api/v1/auth/register",
                  json={"email": email, "password": pw, "name": "dup"})
    _assert_status(r1, 201, "REGISTER #1")
    r2 = _request(c2, "REGISTER #2", "POST", "/api/v1/auth/register",
                  json={"email": email, "password": pw, "name": "dup"})
    _assert_error(r2, 409, "EMAIL_ALREADY_IN_USE", "REGISTER #2")

    # login invalid credentials -> 401
    li = _request(c2, "LOGIN wrong pw", "POST", "/api/v1/auth/login",
                  json={"email": email, "password": "wrong"})
    _assert_error(li, 401, "INVALID_CREDENTIALS", "LOGIN wrong pw")


def test_profile_contract() -> None:
    client = _make_client()
    _register_and_login(client)

    # profile GET before PUT -> 401 USER_NOT_FOUND（あなたの実装仕様）
    g0 = _request(client, "PROFILE GET before", "GET", "/api/v1/profile/me")
    _assert_error(g0, 401, "USER_NOT_FOUND", "PROFILE GET before")

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

    # profile無しで target create -> 404 PROFILE_NOT_FOUND
    t0 = _request(
        client,
        "TARGET create without profile",
        "POST",
        "/api/v1/targets",
        json={"title": "x", "goal_type": "weight_loss",
              "goal_description": None, "activity_level": "normal"},
    )
    _assert_error(t0, 404, "PROFILE_NOT_FOUND",
                  "TARGET create without profile")

    _put_profile(client, meals_per_day=3)

    # create
    t1 = _create_target(client, title="Target 1")
    target_id_1 = t1["id"]
    assert t1["is_active"] is True

    # list
    lst = _request(client, "TARGET list", "GET", "/api/v1/targets")
    _assert_status(lst, 200, "TARGET list")
    assert any(x["id"] == target_id_1 for x in lst.json()), lst.json()

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

    # create second target (inactive)
    t2 = _create_target(client, title="Target 2")
    target_id_2 = t2["id"]
    assert t2["is_active"] is False

    # activate second
    a2 = _request(client, "TARGET activate 2", "POST",
                  f"/api/v1/targets/{target_id_2}/activate")
    _assert_status(a2, 200, "TARGET activate 2")
    assert a2.json()["id"] == target_id_2
    assert a2.json()["is_active"] is True

    # limit exceeded (max=5)
    # already have 2; create 3 more OK, 6th should fail
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

    # list
    lst = _request(client, "MEAL list", "GET",
                   "/api/v1/meal-items", params={"date": d})
    _assert_status(lst, 200, "MEAL list")
    assert any(x["id"] == meal_id for x in lst.json()), lst.json()

    # patch
    upd = _request(client, "MEAL patch", "PATCH",
                   f"/api/v1/meal-items/{meal_id}", json={"name": "Meal 1 updated"})
    _assert_status(upd, 200, "MEAL patch")
    assert upd.json()["entry"]["name"] == "Meal 1 updated"

    # delete
    dele = _request(client, "MEAL delete", "DELETE",
                    f"/api/v1/meal-items/{meal_id}")
    _assert_status(dele, 204, "MEAL delete")

    # not found (patch)
    nf = _request(client, "MEAL patch notfound", "PATCH",
                  "/api/v1/meal-items/00000000-0000-0000-0000-000000000000", json={"name": "x"})
    _assert_error(nf, 404, "FOOD_ENTRY_NOT_FOUND", "MEAL patch notfound")

    # invalid meal_index for main (None)
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

    # invalid food amount (both empty)
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


def test_nutrition_meal_contract_and_plan_gate() -> None:
    # --- normal user (trial) ---
    client = _make_client()
    u = _register_and_login(client)
    _put_profile(client, meals_per_day=3)

    d = date(2025, 1, 2).isoformat()
    for idx in (1, 2, 3):
        _create_meal_item(client, d, "main", idx, f"Meal {idx}")

    # recompute each main slot
    for idx in (1, 2, 3):
        r = _request(
            client,
            f"NUTRITION main#{idx}",
            "GET",
            "/api/v1/nutrition/meal",
            params={"date": d, "meal_type": "main", "meal_index": idx},
        )
        _assert_status(r, 200, f"NUTRITION main#{idx}")
        data = r.json()
        assert "meal" in data and "daily" in data, data
        assert data["meal"]["date"] == d, data
        assert len(data["meal"]["nutrients"]) > 0, data
        assert len(data["daily"]["nutrients"]) > 0, data

    # invalid slot: snack with meal_index -> 400 INVALID_MEAL_INDEX
    bad = _request(
        client,
        "NUTRITION invalid snack index",
        "GET",
        "/api/v1/nutrition/meal",
        params={"date": d, "meal_type": "snack", "meal_index": 1},
    )
    _assert_error(bad, 400, "INVALID_MEAL_INDEX",
                  "NUTRITION invalid snack index")

    # unauth -> 401 INVALID_CREDENTIALS
    anon = _make_client()
    unauth = _request(
        anon,
        "NUTRITION unauth",
        "GET",
        "/api/v1/nutrition/meal",
        params={"date": d, "meal_type": "main", "meal_index": 1},
    )
    _assert_error(unauth, 401, "INVALID_CREDENTIALS", "NUTRITION unauth")

    # --- plan gate (force FREE + expired trial) ---
    gated = _make_client()
    u2 = _register_and_login(gated)
    _force_user_free_plan_and_expired_trial(u2["user_id"])

    # plan check should block first
    g = _request(
        gated,
        "NUTRITION premium required",
        "GET",
        "/api/v1/nutrition/meal",
        params={"date": d, "meal_type": "main", "meal_index": 1},
    )
    _assert_error(g, 403, "PREMIUM_FEATURE_REQUIRED",
                  "NUTRITION premium required")


def test_daily_report_contract_happy_and_errors() -> None:
    client = _make_client()
    u = _register_and_login(client)
    _put_profile(client, meals_per_day=3)
    _create_target(client, title="Target for report")

    d = date(2025, 1, 2).isoformat()

    # meals: only 2/3 -> daily log not completed
    _create_meal_item(client, d, "main", 1, "Meal 1")
    _create_meal_item(client, d, "main", 2, "Meal 2")

    not_completed = _request(
        client,
        "DAILY REPORT not completed",
        "POST",
        "/api/v1/nutrition/daily/report",
        json={"date": d},
    )
    _assert_error(not_completed, 400, "DAILY_LOG_NOT_COMPLETED",
                  "DAILY REPORT not completed")

    # add last meal
    _create_meal_item(client, d, "main", 3, "Meal 3")

    # generate ok
    rep = _request(
        client,
        "DAILY REPORT create",
        "POST",
        "/api/v1/nutrition/daily/report",
        json={"date": d},
    )
    _assert_status(rep, 201, "DAILY REPORT create")
    created = rep.json()
    assert created["date"] == d
    assert isinstance(created.get("summary"),
                      str) and created["summary"].strip()
    assert isinstance(created.get("good_points"),
                      list) and created["good_points"]
    assert isinstance(created.get("improvement_points"),
                      list) and created["improvement_points"]
    assert isinstance(created.get("tomorrow_focus"),
                      list) and created["tomorrow_focus"]

    # already exists -> 409
    rep2 = _request(
        client,
        "DAILY REPORT already exists",
        "POST",
        "/api/v1/nutrition/daily/report",
        json={"date": d},
    )
    _assert_error(rep2, 409, "DAILY_NUTRITION_REPORT_ALREADY_EXISTS",
                  "DAILY REPORT already exists")

    # get ok
    getr = _request(client, "DAILY REPORT get", "GET",
                    "/api/v1/nutrition/daily/report", params={"date": d})
    _assert_status(getr, 200, "DAILY REPORT get")
    fetched = getr.json()
    assert fetched["date"] == d
    assert fetched["summary"] == created["summary"]

    # get missing -> 404 (ここは HTTPException の detail 仕様のままなら detail を確認)
    miss = _request(client, "DAILY REPORT get missing", "GET",
                    "/api/v1/nutrition/daily/report", params={"date": "2025-01-03"})
    assert miss.status_code == 404
    body = miss.json()
    assert "detail" in body, body

    # premium gate
    gated = _make_client()
    u2 = _register_and_login(gated)
    _force_user_free_plan_and_expired_trial(u2["user_id"])
    pg = _request(gated, "DAILY REPORT premium required", "POST",
                  "/api/v1/nutrition/daily/report", json={"date": d})
    _assert_error(pg, 403, "PREMIUM_FEATURE_REQUIRED",
                  "DAILY REPORT premium required")
