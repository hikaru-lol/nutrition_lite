import uuid
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

pytestmark = pytest.mark.real_integration  # このファイル内のテストは real_integration マーク付き


def _make_client() -> TestClient:
    # USE_FAKE_INFRA=false で起動されている前提なので、
    # create_app() は本番と同じ DI (SqlAlchemy + MinIO) で組み立てられる
    app = create_app()
    return TestClient(app)


def _register_user(client: TestClient) -> tuple[str, str]:
    """ユーザー登録を行い、email と user_id を返すヘルパー"""
    email = f"realtest_{uuid.uuid4().hex}@example.com"
    password = "RealTestPassword123!"

    register_resp = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "name": "Real User",
        },
    )

    assert register_resp.status_code == 201, register_resp.text
    data = register_resp.json()
    user_id = data["user"]["id"]
    return email, user_id


def test_register_to_profile_creation_flow_real():
    """
    実際の Postgres + MinIO を使った、ユーザー登録からプロフィール作成までの
    エンドツーエンド統合テスト。

    フロー:
      1. POST /auth/register でユーザー登録
         - Cookie (ACCESS_TOKEN, REFRESH_TOKEN) が発行されることを確認
         - レスポンスにユーザー情報が含まれることを確認
      2. GET /auth/me で認証情報が有効か確認
         - Cookie が正しく機能していることを確認
         - ユーザー情報が正しく取得できることを確認
      3. PUT /profile/me でプロフィール作成
         - プロフィールが正しく作成されることを確認
         - デフォルト値（meals_per_day など）が設定されることを確認
      4. GET /profile/me でプロフィールが永続化されていることを確認
         - 作成したプロフィールが正しく取得できることを確認
      5. PUT /profile/me でプロフィール更新
         - 既存のプロフィールが更新されることを確認
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

    # ステータスコードの確認
    assert register_resp.status_code == 201, (
        f"ユーザー登録が失敗しました: {register_resp.text}"
    )

    # レスポンスボディの確認
    register_data = register_resp.json()
    assert "user" in register_data, "レスポンスに 'user' キーがありません"
    user_data = register_data["user"]
    assert user_data["email"] == email, "メールアドレスが一致しません"
    assert user_data["name"] == name, "名前が一致しません"
    assert "id" in user_data, "ユーザーIDが含まれていません"
    assert "plan" in user_data, "プラン情報が含まれていません"
    assert user_data["plan"] == "trial", "新規登録ユーザーは trial プランであるべきです"

    # Cookie の確認（ACCESS_TOKEN と REFRESH_TOKEN が設定されているか）
    cookies = register_resp.cookies
    assert "ACCESS_TOKEN" in cookies, "ACCESS_TOKEN Cookie が設定されていません"
    assert "REFRESH_TOKEN" in cookies, "REFRESH_TOKEN Cookie が設定されていません"
    assert len(cookies["ACCESS_TOKEN"]) > 0, "ACCESS_TOKEN が空です"
    assert len(cookies["REFRESH_TOKEN"]) > 0, "REFRESH_TOKEN が空です"

    user_id = user_data["id"]

    # ========================================================================
    # 2. 認証情報の確認（/auth/me）
    # ========================================================================
    # TestClient は Set-Cookie を内部の CookieJar に反映してくれるので、
    # 以降のリクエストでは明示的に cookies= を渡さなくても大丈夫。

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
        # meals_per_day は省略（デフォルト値が設定される想定）
    }

    upsert_resp = client.put("/api/v1/profile/me", json=profile_payload)
    assert upsert_resp.status_code == 200, (
        f"プロフィール作成が失敗しました: {upsert_resp.text}"
    )

    profile_data = upsert_resp.json()

    # プロフィールデータの検証
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
    # 画像はまだ API から渡していないので None のはず
    assert profile_data["image_id"] is None, "画像IDは None であるべきです"
    # meals_per_day はデフォルト値が設定されているはず
    assert "meals_per_day" in profile_data, "meals_per_day が含まれていません"
    assert profile_data["meals_per_day"] is not None, (
        "meals_per_day が None です"
    )
    assert 1 <= profile_data["meals_per_day"] <= 6, (
        "meals_per_day が有効な範囲外です"
    )
    # タイムスタンプの確認
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

    # 作成したプロフィールと取得したプロフィールが一致することを確認
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

    # 更新されたデータの確認
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
    assert updated_profile_data["meals_per_day"] == updated_profile_payload["meals_per_day"], (
        "meals_per_day が更新されていません"
    )
    # created_at は変更されず、updated_at は更新されるはず
    assert updated_profile_data["created_at"] == profile_data["created_at"], (
        "created_at は変更されるべきではありません"
    )
    assert updated_profile_data["updated_at"] != profile_data["updated_at"], (
        "updated_at が更新されていません"
    )

    # 更新後のプロフィールを再度取得して確認
    get_updated_resp = client.get("/api/v1/profile/me")
    assert get_updated_resp.status_code == 200, (
        f"更新後のプロフィール取得が失敗しました: {get_updated_resp.text}"
    )
    get_updated_data = get_updated_resp.json()
    assert get_updated_data == updated_profile_data, (
        "更新後のプロフィールが正しく取得できていません"
    )


# def test_profile_access_without_authentication_real():
#     """
#     認証なしでプロフィールにアクセスしようとした場合のエラーテスト。
#     """
#     client = _make_client()

#     # 認証なしでプロフィール取得を試みる
#     get_resp = client.get("/api/v1/profile/me")
#     assert get_resp.status_code == 401, (
#         "認証なしでのアクセスは 401 を返すべきです"
#     )

#     # 認証なしでプロフィール作成を試みる
#     profile_payload = {
#         "sex": "male",
#         "birthdate": "1990-01-02",
#         "height_cm": 175.5,
#         "weight_kg": 68.2,
#     }
#     put_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert put_resp.status_code == 401, (
#         "認証なしでのアクセスは 401 を返すべきです"
#     )


# def test_profile_validation_errors_real():
#     """
#     プロフィール作成時のバリデーションエラーのテスト。
#     """
#     client = _make_client()

#     # ユーザー登録
#     email, user_id = _register_user(client)

#     # 無効な身長（負の値）
#     invalid_resp = client.put(
#         "/api/v1/profile/me",
#         json={
#             "sex": "male",
#             "birthdate": "1990-01-02",
#             "height_cm": -10.0,  # 無効な値
#             "weight_kg": 68.2,
#         },
#     )
#     assert invalid_resp.status_code == 422, (
#         "無効な身長値は 422 を返すべきです"
#     )

#     # 無効な体重（上限超過）
#     invalid_resp2 = client.put(
#         "/api/v1/profile/me",
#         json={
#             "sex": "male",
#             "birthdate": "1990-01-02",
#             "height_cm": 175.5,
#             "weight_kg": 1000.0,  # 上限超過
#         },
#     )
#     assert invalid_resp2.status_code == 422, (
#         "無効な体重値は 422 を返すべきです"
#     )

#     # 無効な meals_per_day（範囲外）
#     invalid_resp3 = client.put(
#         "/api/v1/profile/me",
#         json={
#             "sex": "male",
#             "birthdate": "1990-01-02",
#             "height_cm": 175.5,
#             "weight_kg": 68.2,
#             "meals_per_day": 10,  # 範囲外（1-6の範囲）
#         },
#     )
#     assert invalid_resp3.status_code == 422, (
#         "無効な meals_per_day 値は 422 を返すべきです"
#     )


# def test_target_crud_flow_real():
#     """
#     実際の Postgres を使ったターゲット CRUD のエンドツーエンドテスト。

#     フロー:
#       1. ユーザー登録 & プロフィール作成
#       2. POST /targets でターゲット作成
#       3. GET /targets でターゲット一覧取得
#       4. GET /targets/{target_id} で個別取得
#       5. GET /targets/active でアクティブターゲット取得
#       6. PATCH /targets/{target_id} で更新
#       7. POST /targets/{target_id}/activate でアクティブ化
#     """
#     client = _make_client()

#     # 1. ユーザー登録 & プロフィール作成
#     email, user_id = _register_user(client)

#     profile_payload = {
#         "sex": "male",
#         "birthdate": "1990-01-02",
#         "height_cm": 175.5,
#         "weight_kg": 68.2,
#     }
#     profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert profile_resp.status_code == 200, profile_resp.text

#     # 2. ターゲット作成
#     create_target_resp = client.post(
#         "/api/v1/targets",
#         json={
#             "title": "減量目標",
#             "goal_type": "weight_loss",
#             "goal_description": "5kg減量したい",
#             "activity_level": "normal",
#         },
#     )
#     assert create_target_resp.status_code == 201, create_target_resp.text
#     target_data = create_target_resp.json()
#     assert target_data["title"] == "減量目標"
#     assert target_data["goal_type"] == "weight_loss"
#     assert target_data["is_active"] is True  # 最初のターゲットは自動的にアクティブ
#     assert "nutrients" in target_data
#     assert len(target_data["nutrients"]) > 0
#     target_id = target_data["id"]

#     # 3. ターゲット一覧取得
#     list_resp = client.get("/api/v1/targets")
#     assert list_resp.status_code == 200, list_resp.text
#     list_data = list_resp.json()
#     assert "items" in list_data
#     assert len(list_data["items"]) == 1
#     assert list_data["items"][0]["id"] == target_id

#     # 4. 個別取得
#     get_resp = client.get(f"/api/v1/targets/{target_id}")
#     assert get_resp.status_code == 200, get_resp.text
#     get_data = get_resp.json()
#     assert get_data["id"] == target_id
#     assert get_data["title"] == "減量目標"

#     # 5. アクティブターゲット取得
#     active_resp = client.get("/api/v1/targets/active")
#     assert active_resp.status_code == 200, active_resp.text
#     active_data = active_resp.json()
#     assert active_data["id"] == target_id
#     assert active_data["is_active"] is True

#     # 6. ターゲット更新
#     update_resp = client.patch(
#         f"/api/v1/targets/{target_id}",
#         json={
#             "title": "更新された目標",
#         },
#     )
#     assert update_resp.status_code == 200, update_resp.text
#     update_data = update_resp.json()
#     assert update_data["title"] == "更新された目標"

#     # 7. 2つ目のターゲットを作成してアクティブ化
#     create_target2_resp = client.post(
#         "/api/v1/targets",
#         json={
#             "title": "体重維持目標",
#             "goal_type": "maintain",
#             "goal_description": "現在の体重を維持",
#             "activity_level": "high",
#         },
#     )
#     assert create_target2_resp.status_code == 201, create_target2_resp.text
#     target2_data = create_target2_resp.json()
#     target2_id = target2_data["id"]
#     # 2つ目のターゲットは自動的にアクティブになり、1つ目は非アクティブになる
#     assert target2_data["is_active"] is True

#     # 1つ目のターゲットを再度アクティブ化
#     activate_resp = client.post(f"/api/v1/targets/{target_id}/activate")
#     assert activate_resp.status_code == 200, activate_resp.text
#     activate_data = activate_resp.json()
#     assert activate_data["id"] == target_id
#     assert activate_data["is_active"] is True

#     # 2つ目のターゲットが非アクティブになったことを確認
#     get_target2_resp = client.get(f"/api/v1/targets/{target2_id}")
#     assert get_target2_resp.status_code == 200, get_target2_resp.text
#     assert get_target2_resp.json()["is_active"] is False


# def test_meal_crud_flow_real():
#     """
#     実際の Postgres を使った食事記録 CRUD のエンドツーエンドテスト。

#     フロー:
#       1. ユーザー登録 & プロフィール作成
#       2. POST /meal-items で食事記録作成
#       3. GET /meal-items で一覧取得
#       4. PATCH /meal-items/{entry_id} で更新
#       5. DELETE /meal-items/{entry_id} で削除
#     """
#     client = _make_client()

#     # 1. ユーザー登録 & プロフィール作成
#     email, user_id = _register_user(client)

#     profile_payload = {
#         "sex": "male",
#         "birthdate": "1990-01-02",
#         "height_cm": 175.5,
#         "weight_kg": 68.2,
#     }
#     profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert profile_resp.status_code == 200, profile_resp.text

#     test_date = date.today().isoformat()

#     # 2. 食事記録作成（main meal）
#     create_meal_resp = client.post(
#         "/api/v1/meal-items",
#         json={
#             "date": test_date,
#             "meal_type": "main",
#             "meal_index": 1,
#             "name": "白米",
#             "amount_value": 150.0,
#             "amount_unit": "g",
#             "note": "朝食",
#         },
#     )
#     assert create_meal_resp.status_code == 201, create_meal_resp.text
#     meal_data = create_meal_resp.json()
#     assert meal_data["name"] == "白米"
#     assert meal_data["meal_type"] == "main"
#     assert meal_data["meal_index"] == 1
#     assert "id" in meal_data
#     entry_id = meal_data["id"]

#     # 3. 間食を追加
#     create_snack_resp = client.post(
#         "/api/v1/meal-items",
#         json={
#             "date": test_date,
#             "meal_type": "snack",
#             "meal_index": None,
#             "name": "りんご",
#             "amount_value": 1.0,
#             "amount_unit": "個",
#         },
#     )
#     assert create_snack_resp.status_code == 201, create_snack_resp.text
#     snack_data = create_snack_resp.json()
#     assert snack_data["meal_type"] == "snack"
#     assert snack_data["meal_index"] is None

#     # 4. 一覧取得
#     list_resp = client.get(f"/api/v1/meal-items?date={test_date}")
#     assert list_resp.status_code == 200, list_resp.text
#     list_data = list_resp.json()
#     assert "items" in list_data
#     assert len(list_data["items"]) == 2

#     # 5. 更新
#     update_resp = client.patch(
#         f"/api/v1/meal-items/{entry_id}",
#         json={
#             "date": test_date,
#             "meal_type": "main",
#             "meal_index": 1,
#             "name": "玄米",
#             "amount_value": 150.0,
#             "amount_unit": "g",
#             "note": "更新された朝食",
#         },
#     )
#     assert update_resp.status_code == 200, update_resp.text
#     update_data = update_resp.json()
#     assert update_data["name"] == "玄米"
#     assert update_data["note"] == "更新された朝食"

#     # 6. 削除
#     delete_resp = client.delete(f"/api/v1/meal-items/{entry_id}")
#     assert delete_resp.status_code == 204, delete_resp.text

#     # 削除後、一覧から消えていることを確認
#     list_after_delete_resp = client.get(f"/api/v1/meal-items?date={test_date}")
#     assert list_after_delete_resp.status_code == 200, list_after_delete_resp.text
#     list_after_delete_data = list_after_delete_resp.json()
#     assert len(list_after_delete_data["items"]) == 1  # 間食のみ残る


# def test_nutrition_computation_flow_real():
#     """
#     実際の Postgres を使った栄養計算のエンドツーエンドテスト。

#     フロー:
#       1. ユーザー登録 & プロフィール作成
#       2. ターゲット作成
#       3. 食事記録作成
#       4. GET /nutrition/meal で栄養計算
#     """
#     client = _make_client()

#     # 1. ユーザー登録 & プロフィール作成
#     email, user_id = _register_user(client)

#     profile_payload = {
#         "sex": "male",
#         "birthdate": "1990-01-02",
#         "height_cm": 175.5,
#         "weight_kg": 68.2,
#     }
#     profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert profile_resp.status_code == 200, profile_resp.text

#     # 2. ターゲット作成
#     create_target_resp = client.post(
#         "/api/v1/targets",
#         json={
#             "title": "減量目標",
#             "goal_type": "weight_loss",
#             "goal_description": "5kg減量",
#             "activity_level": "normal",
#         },
#     )
#     assert create_target_resp.status_code == 201, create_target_resp.text

#     test_date = date.today().isoformat()

#     # 3. 食事記録作成
#     create_meal_resp = client.post(
#         "/api/v1/meal-items",
#         json={
#             "date": test_date,
#             "meal_type": "main",
#             "meal_index": 1,
#             "name": "白米",
#             "amount_value": 150.0,
#             "amount_unit": "g",
#         },
#     )
#     assert create_meal_resp.status_code == 201, create_meal_resp.text

#     # 4. 栄養計算
#     nutrition_resp = client.get(
#         f"/api/v1/nutrition/meal?date={test_date}&meal_type=main&meal_index=1"
#     )
#     assert nutrition_resp.status_code == 200, nutrition_resp.text
#     nutrition_data = nutrition_resp.json()
#     assert "meal" in nutrition_data
#     assert "daily" in nutrition_data

#     # 食事の栄養サマリを確認
#     meal_summary = nutrition_data["meal"]
#     assert meal_summary["date"] == test_date
#     assert meal_summary["meal_type"] == "main"
#     assert meal_summary["meal_index"] == 1
#     assert "nutrients" in meal_summary
#     assert len(meal_summary["nutrients"]) > 0

#     # 日次の栄養サマリを確認
#     daily_summary = nutrition_data["daily"]
#     assert daily_summary["date"] == test_date
#     assert "nutrients" in daily_summary
#     assert len(daily_summary["nutrients"]) > 0


# def test_daily_report_flow_real():
#     """
#     実際の Postgres を使った日次レポート生成のエンドツーエンドテスト。

#     フロー:
#       1. ユーザー登録 & プロフィール作成
#       2. ターゲット作成
#       3. 食事記録作成（記録完了状態にする）
#       4. POST /nutrition/daily/report でレポート生成
#       5. GET /nutrition/daily/report でレポート取得
#     """
#     client = _make_client()

#     # 1. ユーザー登録 & プロフィール作成
#     email, user_id = _register_user(client)

#     profile_payload = {
#         "sex": "male",
#         "birthdate": "1990-01-02",
#         "height_cm": 175.5,
#         "weight_kg": 68.2,
#     }
#     profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert profile_resp.status_code == 200, profile_resp.text
#     profile_data = profile_resp.json()
#     meals_per_day = profile_data.get("meals_per_day", 3)

#     # 2. ターゲット作成
#     create_target_resp = client.post(
#         "/api/v1/targets",
#         json={
#             "title": "減量目標",
#             "goal_type": "weight_loss",
#             "goal_description": "5kg減量",
#             "activity_level": "normal",
#         },
#     )
#     assert create_target_resp.status_code == 201, create_target_resp.text

#     test_date = date.today().isoformat()

#     # 3. 食事記録作成（記録完了にするため、必要な分だけ作成）
#     # プロフィールの meals_per_day に応じて main meal を作成
#     for i in range(1, meals_per_day + 1):
#         create_meal_resp = client.post(
#             "/api/v1/meal-items",
#             json={
#                 "date": test_date,
#                 "meal_type": "main",
#                 "meal_index": i,
#                 "name": f"食事{i}",
#                 "amount_value": 100.0,
#                 "amount_unit": "g",
#             },
#         )
#         assert create_meal_resp.status_code == 201, create_meal_resp.text

#     # 4. レポート生成
#     generate_resp = client.post(
#         "/api/v1/nutrition/daily/report",
#         json={"date": test_date},
#     )
#     assert generate_resp.status_code == 201, generate_resp.text
#     report_data = generate_resp.json()
#     assert report_data["date"] == test_date
#     assert "summary" in report_data
#     assert "good_points" in report_data
#     assert "improvement_points" in report_data
#     assert "tomorrow_focus" in report_data
#     assert isinstance(report_data["good_points"], list)
#     assert isinstance(report_data["improvement_points"], list)
#     assert isinstance(report_data["tomorrow_focus"], list)

#     # 5. レポート取得
#     get_resp = client.get(f"/api/v1/nutrition/daily/report?date={test_date}")
#     assert get_resp.status_code == 200, get_resp.text
#     get_report_data = get_resp.json()
#     assert get_report_data["date"] == test_date
#     assert get_report_data["summary"] == report_data["summary"]


# def test_complete_user_journey_real():
#     """
#     実際の Postgres を使った完全なユーザージャーニーのエンドツーエンドテスト。

#     フロー:
#       1. ユーザー登録
#       2. プロフィール作成
#       3. ターゲット作成
#       4. 食事記録作成
#       5. 栄養計算
#       6. 日次レポート生成
#       7. レポート取得
#     """
#     client = _make_client()

#     # 1. ユーザー登録
#     email, user_id = _register_user(client)

#     # 2. プロフィール作成
#     profile_payload = {
#         "sex": "female",
#         "birthdate": "1995-06-15",
#         "height_cm": 160.0,
#         "weight_kg": 55.0,
#     }
#     profile_resp = client.put("/api/v1/profile/me", json=profile_payload)
#     assert profile_resp.status_code == 200, profile_resp.text
#     profile_data = profile_resp.json()
#     meals_per_day = profile_data.get("meals_per_day", 3)

#     # 3. ターゲット作成
#     create_target_resp = client.post(
#         "/api/v1/targets",
#         json={
#             "title": "健康改善目標",
#             "goal_type": "health_improve",
#             "goal_description": "バランスの良い食事を心がける",
#             "activity_level": "normal",
#         },
#     )
#     assert create_target_resp.status_code == 201, create_target_resp.text
#     target_data = create_target_resp.json()
#     assert target_data["is_active"] is True

#     test_date = date.today().isoformat()

#     # 4. 食事記録作成
#     meal_items = []
#     for i in range(1, meals_per_day + 1):
#         create_meal_resp = client.post(
#             "/api/v1/meal-items",
#             json={
#                 "date": test_date,
#                 "meal_type": "main",
#                 "meal_index": i,
#                 "name": f"メイン食事{i}",
#                 "amount_value": 200.0,
#                 "amount_unit": "g",
#                 "note": f"{i}回目の食事",
#             },
#         )
#         assert create_meal_resp.status_code == 201, create_meal_resp.text
#         meal_items.append(create_meal_resp.json())

#     # 間食も追加
#     create_snack_resp = client.post(
#         "/api/v1/meal-items",
#         json={
#             "date": test_date,
#             "meal_type": "snack",
#             "meal_index": None,
#             "name": "バナナ",
#             "amount_value": 1.0,
#             "amount_unit": "本",
#         },
#     )
#     assert create_snack_resp.status_code == 201, create_snack_resp.text

#     # 5. 栄養計算（1つ目の食事）
#     nutrition_resp = client.get(
#         f"/api/v1/nutrition/meal?date={test_date}&meal_type=main&meal_index=1"
#     )
#     assert nutrition_resp.status_code == 200, nutrition_resp.text
#     nutrition_data = nutrition_resp.json()
#     assert "meal" in nutrition_data
#     assert "daily" in nutrition_data

#     # 6. 日次レポート生成
#     generate_resp = client.post(
#         "/api/v1/nutrition/daily/report",
#         json={"date": test_date},
#     )
#     assert generate_resp.status_code == 201, generate_resp.text
#     report_data = generate_resp.json()
#     assert report_data["date"] == test_date
#     assert len(report_data["summary"]) > 0

#     # 7. レポート取得
#     get_resp = client.get(f"/api/v1/nutrition/daily/report?date={test_date}")
#     assert get_resp.status_code == 200, get_resp.text
#     get_report_data = get_resp.json()
#     assert get_report_data == report_data

#     # 8. 最終確認: 食事記録一覧
#     list_resp = client.get(f"/api/v1/meal-items?date={test_date}")
#     assert list_resp.status_code == 200, list_resp.text
#     list_data = list_resp.json()
#     assert len(list_data["items"]) == meals_per_day + 1  # main meals + snack
