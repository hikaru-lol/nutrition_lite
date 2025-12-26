from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

# === Application (DTO / Ports / UseCase) ====================================

from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.dto.register_dto import RegisterInputDTO, RegisterOutputDTO
from app.application.auth.ports.clock_port import ClockPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import (
    TokenPayload,
    TokenPair,
    TokenServicePort,
)
from app.application.auth.ports.uow_port import AuthUnitOfWorkPort

# === Domain (Entities / ValueObjects / Errors) ==============================

from app.domain.auth.entities import User
from app.domain.auth.errors import EmailAlreadyUsedError
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    TrialInfo,
    UserId,
    UserPlan,
)


class RegisterUserUseCase:
    """
    新規ユーザー登録を行うユースケース。

    フロー:
        1. メールアドレス重複チェック
        2. パスワードハッシュ化 + User エンティティ生成
        3. User を永続化
        4. トライアルプラン情報を付与したトークンペアを発行
        5. AuthUserDTO + TokenPair を含む RegisterOutputDTO を返す
    """

    def __init__(
        self,
        uow: AuthUnitOfWorkPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
        clock: ClockPort,
    ) -> None:
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._clock = clock

    def execute(self, input_dto: RegisterInputDTO) -> RegisterOutputDTO:
        """
        ユーザー登録を実行する。

        Raises:
            EmailAlreadyUsedError: 同じメールアドレスのユーザーが既に存在する場合
        """
        email_vo = EmailAddress(input_dto.email)

        now = self._clock.now()
        trial_ends_at = now + timedelta(days=7)

        # 1ユースケース = 1トランザクション (AuthUnitOfWorkPort)
        with self._uow as uow:
            # --- 1. 重複チェック --------------------------------------
            if uow.user_repo.get_by_email(email_vo) is not None:
                # ここで例外が出れば __exit__ 側で rollback される
                raise EmailAlreadyUsedError("Email is already registered.")

            # --- 2. ユーザー作成 --------------------------------------
            hashed_password: HashedPassword = self._password_hasher.hash(
                input_dto.password
            )

            user = User(
                id=UserId(str(uuid4())),
                email=email_vo,
                hashed_password=hashed_password,
                name=input_dto.name,
                plan=UserPlan.TRIAL,
                trial_info=TrialInfo(trial_ends_at=trial_ends_at),
                has_profile=False,
                created_at=now,
            )

            saved = uow.user_repo.save(user)

        # --- 3. トークン発行 ------------------------------------------
        payload = TokenPayload(user_id=saved.id.value, plan=saved.plan)
        tokens: TokenPair = self._token_service.issue_tokens(payload)

        # --- 4. DTO に詰めて返却 --------------------------------------
        return RegisterOutputDTO(
            user=AuthUserDTO.from_entity(saved),
            tokens=tokens,
        )
