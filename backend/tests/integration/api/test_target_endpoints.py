from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
import pytest
from fastapi.testclient import TestClient

from app.domain.target.value_objects import NutrientCode
from app.di.container import (
    get_create_target_use_case,
    get_list_targets_use_case,
    get_get_target_use_case,
    get_get_active_target_use_case,
    get_update_target_use_case,
    get_activate_target_use_case,
)
from app.application.target.use_cases.create_target import CreateTargetUseCase
from app.application.target.use_cases.list_targets import ListTargetsUseCase
from app.application.target.use_cases.get_target import GetTargetUseCase
from app.application.target.use_cases.get_active_target import (
    GetActiveTargetUseCase,
)
from app.application.target.use_cases.update_target import UpdateTargetUseCase
from app.application.target.use_cases.activate_target import (
    ActivateTargetUseCase,
)
from app.application.target.ports.uow_port import TargetUnitOfWorkPort

# ユニットテストで使っている Fake を再利用
from tests.unit.application.target.fakes import (
    FakeTargetRepository,
    FakeTargetSnapshotRepository,
    FakeTargetUnitOfWork,
    FakeTargetGenerator,
)


@pytest.fixture
def target_client(app: FastAPI) -> TestClient:
    """
    conftest.py の app fixture（auth/profile の Fake DI 済み）をベースに、
    Target 用だけ Fake UoW / Fake Generator に差し替えた TestClient を返す。
    """
    # Target 用のインメモリ Repo / SnapshotRepo / Generator
    target_repo = FakeTargetRepository()
    snapshot_repo = FakeTargetSnapshotRepository()
    generator = FakeTargetGenerator()

    def make_target_uow() -> TargetUnitOfWorkPort:
        # UoW は毎回新しく作るが、内部の Repo は同じものを共有
        return FakeTargetUnitOfWork(
            target_repo=target_repo,
            target_snapshot_repo=snapshot_repo,
        )

    # --- Target UseCase の DI を Fake に override ---------------------

    app.dependency_overrides[get_create_target_use_case] = (
        lambda: CreateTargetUseCase(
            uow=make_target_uow(),
            generator=generator,
        )
    )

    app.dependency_overrides[get_list_targets_use_case] = (
        lambda: ListTargetsUseCase(
            uow=make_target_uow(),
        )
    )

    app.dependency_overrides[get_get_target_use_case] = (
        lambda: GetTargetUseCase(
            uow=make_target_uow(),
        )
    )

    app.dependency_overrides[get_get_active_target_use_case] = (
        lambda: GetActiveTargetUseCase(
            uow=make_target_uow(),
        )
    )

    app.dependency_overrides[get_update_target_use_case] = (
        lambda: UpdateTargetUseCase(
            uow=make_target_uow(),
        )
    )

    app.dependency_overrides[get_activate_target_use_case] = (
        lambda: ActivateTargetUseCase(
            uow=make_target_uow(),
        )
    )

    client = TestClient(app)

    try:
        yield client
    finally:
        # 他のテストに影響を残さないよう、Target 用 override だけ消しておく
        for dep in (
            get_create_target_use_case,
            get_list_targets_use_case,
            get_get_target_use_case,
            get_get_active_target_use_case,
            get_update_target_use_case,
            get_activate_target_use_case,
        ):
            app.dependency_overrides.pop(dep, None)


def _register_user(client: TestClient) -> None:
    """
    テスト用ユーザーを 1 人登録して、クッキーをセットしておく。
    """
    email = f"user-{uuid4()}@example.com"
    res = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",  # 8文字以上
            "name": "Test User",
        },
    )
    assert res.status_code == 201, res.text
    # set_auth_cookies により ACCESS_TOKEN / REFRESH_TOKEN がセットされるので、
    # この client でそのまま /targets を叩けば認証済みとして扱われる。


def test_create_list_get_active_target_flow(target_client: TestClient):
    client = target_client

    # 1. ユーザー登録（= ログイン状態にする）
    _register_user(client)

    # 2. ターゲット作成
    payload = {
        "title": "My First Target",
        "goal_type": "weight_loss",
        "goal_description": "ダイエット用",
        "activity_level": "normal",
    }

    res = client.post("/api/v1/targets", json=payload)
    assert res.status_code == 201, res.text
    created = res.json()
    target_id = created["id"]

    assert created["title"] == "My First Target"
    assert created["goal_type"] == "weight_loss"
    assert created["activity_level"] == "normal"
    assert created["is_active"] is True

    # nutrients の数が 17 種類ぶんあること
    assert len(created["nutrients"]) == len(list(NutrientCode))

    # 3. 一覧取得
    res = client.get("/api/v1/targets")
    assert res.status_code == 200, res.text
    listed = res.json()
    assert "items" in listed
    assert len(listed["items"]) == 1
    assert listed["items"][0]["id"] == target_id

    # 4. ID指定で取得
    res = client.get(f"/api/v1/targets/{target_id}")
    assert res.status_code == 200, res.text
    detail = res.json()
    assert detail["id"] == target_id
    assert detail["title"] == "My First Target"

    # 5. アクティブターゲット取得
    res = client.get("/api/v1/targets/active")
    assert res.status_code == 200, res.text
    active = res.json()
    assert active["id"] == target_id
    assert active["is_active"] is True


def test_update_target_via_api(target_client: TestClient):
    client = target_client
    _register_user(client)

    # まず1件作成
    res = client.post(
        "/api/v1/targets",
        json={
            "title": "Before",
            "goal_type": "weight_loss",
            "goal_description": None,
            "activity_level": "low",
        },
    )
    assert res.status_code == 201, res.text
    target_id = res.json()["id"]

    # PATCH で PFC とメタ情報を更新
    patch_payload = {
        "title": "After",
        "goal_type": "maintain",
        "goal_description": "維持フェーズ",
        "activity_level": "high",
        "llm_rationale": "Updated rationale",
        "disclaimer": "Updated disclaimer",
        "nutrients": [
            {
                "code": "protein",
                "amount": 200.0,
                "unit": "g",
            }
        ],
    }

    res = client.patch(f"/api/v1/targets/{target_id}", json=patch_payload)
    assert res.status_code == 200, res.text
    updated = res.json()

    assert updated["title"] == "After"
    assert updated["goal_type"] == "maintain"
    assert updated["activity_level"] == "high"
    assert updated["llm_rationale"] == "Updated rationale"

    # protein の nutrient が 200g / manual になっていること
    protein = next(
        n for n in updated["nutrients"] if n["code"] == "protein"
    )
    assert protein["amount"] == 200.0
    assert protein["unit"] == "g"
    assert protein["source"] == "manual"


def test_activate_target_flow(target_client: TestClient):
    client = target_client
    _register_user(client)

    # 1件目（自動的に active）
    res1 = client.post(
        "/api/v1/targets",
        json={
            "title": "First",
            "goal_type": "maintain",
            "goal_description": None,
            "activity_level": "normal",
        },
    )
    assert res1.status_code == 201, res1.text
    first_id = res1.json()["id"]
    assert res1.json()["is_active"] is True

    # 2件目（既に active があるので is_active=False のはず）
    res2 = client.post(
        "/api/v1/targets",
        json={
            "title": "Second",
            "goal_type": "weight_gain",
            "goal_description": None,
            "activity_level": "high",
        },
    )
    assert res2.status_code == 201, res2.text
    second_id = res2.json()["id"]
    assert res2.json()["is_active"] is False

    # /targets/{id}/activate で 2件目をアクティブ化
    res3 = client.post(f"/api/v1/targets/{second_id}/activate")
    assert res3.status_code == 200, res3.text
    activated = res3.json()
    assert activated["id"] == second_id
    assert activated["is_active"] is True

    # /targets/active でも 2件目が返る
    res4 = client.get("/api/v1/targets/active")
    assert res4.status_code == 200, res4.text
    active = res4.json()
    assert active["id"] == second_id
    assert active["is_active"] is True


def test_get_target_not_found_returns_404(target_client: TestClient):
    client = target_client
    _register_user(client)

    random_id = str(uuid4())
    res = client.get(f"/api/v1/targets/{random_id}")

    assert res.status_code == 404
    body = res.json()
    assert "error" in body
    assert body["error"]["code"] in (
        "TARGET_NOT_FOUND", "ACTIVE_TARGET_NOT_FOUND")
    # （Active 専用コードを分けていれば ACTIVE_TARGET_NOT_FOUND も許容）


def test_update_invalid_nutrient_code_returns_400(target_client: TestClient):
    client = target_client
    _register_user(client)

    # まず 1件作成
    res = client.post(
        "/api/v1/targets",
        json={
            "title": "Target",
            "goal_type": "maintain",
            "goal_description": None,
            "activity_level": "normal",
        },
    )
    assert res.status_code == 201, res.text
    target_id = res.json()["id"]

    # 存在しない code で PATCH
    patch_payload = {
        "nutrients": [
            {
                "code": "unknown_nutrient",
                "amount": 100.0,
                "unit": "g",
            }
        ]
    }

    res = client.patch(f"/api/v1/targets/{target_id}", json=patch_payload)
    assert res.status_code == 400
    body = res.json()
    assert "error" in body
    # handler 側で INVALID_TARGET_NUTRIENT を返す実装にしておくこと
    assert body["error"]["code"] == "INVALID_TARGET_NUTRIENT"
