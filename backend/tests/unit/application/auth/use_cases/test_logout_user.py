from __future__ import annotations

from app.application.auth.use_cases.session.logout_user import LogoutUserUseCase


def test_logout_user_noop():
    use_case = LogoutUserUseCase()

    # 現状は No-Op。例外が出ないことだけ確認。
    use_case.execute(user_id="some-user-id")
