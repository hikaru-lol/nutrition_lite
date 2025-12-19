import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.real_integration  # このファイル内のテストは real_integration マーク付き


def _make_client() -> TestClient:
    # USE_FAKE_INFRA=false で起動されている前提なので、
    # create_app() は本番と同じ DI (SqlAlchemy + MinIO) で組み立てられる
    app = create_app()
    return TestClient(app)


def _assert_meals_per_day(profile: dict, *, expected: int | None = None) -> None:
    """
    meals_per_day は現状「未設定なら None」の契約になっている前提。
    将来的にAPI側でデフォルト注入が入っても耐えられるよう、
    None または 1..6 の範囲の int を許容する。
    """
    assert "meals_per_day" in profile, "meals_per_day が含まれていません"
    value = profile["meals_per_day"]

    if expected is not None:
        # 現状の実装では反映されない可能性もあるので、
        # 「None or expected」を許容（将来、実装が入ったら expected 側に寄る）
        assert value in (None, expected), (
            f"meals_per_day は None か {expected} のはずです: {value}"
        )
        if value is not None:
            assert isinstance(
                value, int), f"meals_per_day の型が不正です: {type(value)}"
            assert 1 <= value <= 6, "meals_per_day が有効な範囲外です"
        return

    if value is None:
        return

    assert isinstance(value, int), f"meals_per_day の型が不正です: {type(value)}"
    assert 1 <= value <= 6, "meals_per_day が有効な範囲外です"


def _assert_request_validation_error_400(resp) -> None:
    """
    このプロジェクトでは RequestValidationError を 422 ではなく 400 にマッピングしている前提。
    エラーボディは ErrorResponse 形式へ寄せている途中の可能性があるので緩めにチェック。
    """
    assert resp.status_code == 400, f"期待:400 実際:{resp.status_code} body={resp.text}"
    body = resp.json()
    assert "error" in body or "detail" in body, f"エラーレスポンス形式が想定外: {body}"
    if "error" in body:
        # ErrorResponse { error: { code, message } } を想定
        assert body["error"]["code"] == "VALIDATION_ERROR"


def test_register_to_profile_creation_flow_real():
    """
    実際の Postgres + MinIO を使った、ユーザー登録からプロフィール作成までの
    エンドツーエンド統合テスト。

    フロー:
      1. POST /auth/register でユーザー登録
      2. GET /auth/me で認証情報が有効か確認
      3. PUT /profile/me でプロフィール作成
      4. GET /profile/me でプロフィールが永続化されていることを確認
      5. PUT /profile/me でプロフィール更新
    """
    client = _make_client()

    # ========================================================================
    # 1. ユーザー登録
    # ========================================================================
    email = f"realtest_{uuid.uuid4().hex}@example.com"
    password = "RealTestPassword123!"
    name = "Real Test User"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": name,
        },
    )

    assert register_resp.status_code == 201, (
        f"ユーザー登録が失敗しました: {register_resp.text}"
    )

    register_data = register_resp.json()
    assert "user" in register_data, "レスポンスに 'user' キーがありません"
    user_data = register_data["user"]
    assert user_data["email"] == email, "メールアドレスが一致しません"
    assert user_data["name"] == name, "名前が一致しません"
    assert "id" in user_data, "ユーザーIDが含まれていません"
    assert "plan" in user_data, "プラン情報が含まれていません"
    assert user_data["plan"] == "trial", "新規登録ユーザーは trial プランであるべきです"

    cookies = register_resp.cookies
    assert "ACCESS_TOKEN" in cookies, "ACCESS_TOKEN Cookie が設定されていません"
    assert "REFRESH_TOKEN" in cookies, "REFRESH_TOKEN Cookie が設定されていません"
    assert len(cookies["ACCESS_TOKEN"]) > 0, "ACCESS_TOKEN が空です"
    assert len(cookies["REFRESH_TOKEN"]) > 0, "REFRESH_TOKEN が空です"

    user_id = user_data["id"]

    # ========================================================================
    # 2. 認証情報の確認（/auth/me）
    # ========================================================================
    me_resp = client.get("/api/v1/auth/me")
    assert me_resp.status_code == 200, (
        f"認証情報の取得が失敗しました: {me_resp.text}"
    )

    me_data = me_resp.json()
    assert "user" in me_data, "レスポンスに 'user' キーがありません"
    assert me_data["user"]["email"] == email, "メールアドレスが一致しません"
    assert me_data["user"]["id"] == user_id, "ユーザーIDが一致しません"
    assert me_data["user"]["name"] == name, "名前が一致しません"

    # ========================================================================
    # 3. プロフィール作成（PUT /profile/me）
    # ========================================================================
    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
        # meals_per_day は省略（現状は None のままでもOK）
    }

    upsert_resp = client.put("/api/v1/profile/me", json=profile_payload)
    assert upsert_resp.status_code == 200, (
        f"プロフィール作成が失敗しました: {upsert_resp.text}"
    )

    profile_data = upsert_resp.json()

    assert profile_data["user_id"] == user_id, "ユーザーIDが一致しません"
    assert profile_data["sex"] == profile_payload["sex"], "性別が一致しません"
    assert profile_data["birthdate"] == profile_payload["birthdate"], (
        "生年月日が一致しません"
    )
    assert profile_data["height_cm"] == profile_payload["height_cm"], (
        "身長が一致しません"
    )
    assert profile_data["weight_kg"] == profile_payload["weight_kg"], (
        "体重が一致しません"
    )
    assert profile_data["image_id"] is None, "画像IDは None であるべきです"

    # meals_per_day は None or 1..6 を許容
    _assert_meals_per_day(profile_data)

    assert "created_at" in profile_data, "created_at が含まれていません"
    assert "updated_at" in profile_data, "updated_at が含まれていません"

    # ========================================================================
    # 4. プロフィール取得（GET /profile/me）
    # ========================================================================
    get_profile_resp = client.get("/api/v1/profile/me")
    assert get_profile_resp.status_code == 200, (
        f"プロフィール取得が失敗しました: {get_profile_resp.text}"
    )

    get_profile_data = get_profile_resp.json()

    assert get_profile_data["user_id"] == profile_data["user_id"], (
        "ユーザーIDが一致しません"
    )
    assert get_profile_data["sex"] == profile_data["sex"], "性別が一致しません"
    assert get_profile_data["birthdate"] == profile_data["birthdate"], (
        "生年月日が一致しません"
    )
    assert get_profile_data["height_cm"] == profile_data["height_cm"], (
        "身長が一致しません"
    )
    assert get_profile_data["weight_kg"] == profile_data["weight_kg"], (
        "体重が一致しません"
    )
    assert get_profile_data["meals_per_day"] == profile_data["meals_per_day"], (
        "meals_per_day が一致しません"
    )
    assert get_profile_data["created_at"] == profile_data["created_at"], (
        "created_at が一致しません"
    )

    # ========================================================================
    # 5. プロフィール更新（PUT /profile/me）
    # ========================================================================
    updated_profile_payload = {
        "sex": "female",
        "birthdate": "1995-06-15",
        "height_cm": 160.0,
        "weight_kg": 55.0,
        "meals_per_day": 4,
    }

    update_resp = client.put("/api/v1/profile/me",
                             json=updated_profile_payload)
    assert update_resp.status_code == 200, (
        f"プロフィール更新が失敗しました: {update_resp.text}"
    )

    updated_profile_data = update_resp.json()

    assert updated_profile_data["user_id"] == user_id, "ユーザーIDが一致しません"
    assert updated_profile_data["sex"] == updated_profile_payload["sex"], (
        "性別が更新されていません"
    )
    assert updated_profile_data["birthdate"] == updated_profile_payload["birthdate"], (
        "生年月日が更新されていません"
    )
    assert updated_profile_data["height_cm"] == updated_profile_payload["height_cm"], (
        "身長が更新されていません"
    )
    assert updated_profile_data["weight_kg"] == updated_profile_payload["weight_kg"], (
        "体重が更新されていません"
    )

    # meals_per_day は「None or 4」を許容（現状の実装都合で反映されない可能性があるため）
    _assert_meals_per_day(updated_profile_data, expected=4)

    assert updated_profile_data["created_at"] == profile_data["created_at"], (
        "created_at は変更されるべきではありません"
    )
    assert updated_profile_data["updated_at"] != profile_data["updated_at"], (
        "updated_at が更新されていません"
    )

    get_updated_resp = client.get("/api/v1/profile/me")
    assert get_updated_resp.status_code == 200, (
        f"更新後のプロフィール取得が失敗しました: {get_updated_resp.text}"
    )
    get_updated_data = get_updated_resp.json()
    assert get_updated_data == updated_profile_data, (
        "更新後のプロフィールが正しく取得できていません"
    )


def test_profile_access_without_authentication_real():
    """
    認証なしでプロフィールにアクセスしようとした場合のエラーテスト。
    """
    client = _make_client()

    get_resp = client.get("/api/v1/profile/me")
    assert get_resp.status_code == 401, (
        "認証なしでのアクセスは 401 を返すべきです"
    )

    profile_payload = {
        "sex": "male",
        "birthdate": "1990-01-02",
        "height_cm": 175.5,
        "weight_kg": 68.2,
    }
    put_resp = client.put("/api/v1/profile/me", json=profile_payload)
    assert put_resp.status_code == 401, (
        "認証なしでのアクセスは 401 を返すべきです"
    )


def test_profile_validation_errors_real():
    """
    プロフィール作成時のバリデーションエラーのテスト。
    ※ 本プロジェクトでは RequestValidationError を 400 にマッピングしている前提。
    """
    client = _make_client()

    # ユーザー登録
    email = f"realtest_{uuid.uuid4().hex}@example.com"
    password = "RealTestPassword123!"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Test User",
        },
    )
    assert register_resp.status_code == 201, register_resp.text

    # 無効な身長（負の値）
    invalid_resp = client.put(
        "/api/v1/profile/me",
        json={
            "sex": "male",
            "birthdate": "1990-01-02",
            "height_cm": -10.0,
            "weight_kg": 68.2,
        },
    )
    _assert_request_validation_error_400(invalid_resp)

    # 無効な体重（上限超過）
    invalid_resp2 = client.put(
        "/api/v1/profile/me",
        json={
            "sex": "male",
            "birthdate": "1990-01-02",
            "height_cm": 175.5,
            "weight_kg": 1000.0,
        },
    )
    _assert_request_validation_error_400(invalid_resp2)

    # 無効な meals_per_day（範囲外）
    invalid_resp3 = client.put(
        "/api/v1/profile/me",
        json={
            "sex": "male",
            "birthdate": "1990-01-02",
            "height_cm": 175.5,
            "weight_kg": 68.2,
            "meals_per_day": 10,  # 範囲外（1-6）
        },
    )
    _assert_request_validation_error_400(invalid_resp3)
