from __future__ import annotations

from datetime import timedelta
from uuid import uuid4

from app.application.auth.dto.register_dto import RegisterInputDTO, RegisterOutputDTO
from app.application.auth.dto.auth_user_dto import AuthUserDTO
from app.application.auth.ports.user_repository_port import UserRepositoryPort
from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.application.auth.ports.token_service_port import TokenServicePort, TokenPayload, TokenPair
from app.application.auth.ports.clock_port import ClockPort
from app.domain.auth.entities import User
from app.domain.auth.value_objects import (
    EmailAddress,
    HashedPassword,
    UserId,
    UserPlan,
    TrialInfo,
)


class EmailAlreadyUsedError(Exception):
    pass


class RegisterUserUseCase:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
        clock: ClockPort,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._clock = clock

    def execute(self, input_dto: RegisterInputDTO) -> RegisterOutputDTO:
        email_vo = EmailAddress(input_dto.email)

        if self._user_repo.get_by_email(email_vo) is not None:
            raise EmailAlreadyUsedError("Email is already registered.")

        hashed: HashedPassword = self._password_hasher.hash(input_dto.password)

        now = self._clock.now()
        trial_ends_at = now + timedelta(days=7)

        user = User(
            id=UserId(str(uuid4())),
            email=email_vo,
            hashed_password=hashed,
            name=input_dto.name,
            plan=UserPlan.TRIAL,
            trial_info=TrialInfo(trial_ends_at=trial_ends_at),
            has_profile=False,
            created_at=now,
        )

        saved = self._user_repo.save(user)

        payload = TokenPayload(user_id=saved.id.value, plan=saved.plan)
        tokens: TokenPair = self._token_service.issue_tokens(payload)

        return RegisterOutputDTO(
            user=AuthUserDTO.from_entity(saved),
            tokens=tokens,
        )
