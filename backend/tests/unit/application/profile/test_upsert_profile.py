from __future__ import annotations

from datetime import date

from app.application.profile.dto.profile_dto import UpsertProfileInputDTO
from app.application.profile.use_cases.upsert_profile import UpsertProfileUseCase
from app.domain.profile.value_objects import Sex
from app.domain.auth.value_objects import UserId
from tests.fakes.profile_repositories import InMemoryProfileRepository
from tests.fakes.profile_uow import FakeProfileUnitOfWork
from app.infra.storage.profile_image_storage import InMemoryProfileImageStorage


def _make_use_case(repo: InMemoryProfileRepository) -> UpsertProfileUseCase:
    uow = FakeProfileUnitOfWork(profile_repo=repo)
    storage = InMemoryProfileImageStorage()
    return UpsertProfileUseCase(uow=uow, image_storage=storage)


def test_upsert_profile_creates_new_profile() -> None:
    repo = InMemoryProfileRepository()
    use_case = _make_use_case(repo)

    input_dto = UpsertProfileInputDTO(
        user_id="11111111-1111-1111-1111-111111111111",
        sex=Sex.MALE,
        birthdate=date(1990, 1, 1),
        height_cm=175.0,
        weight_kg=70.5,
        image_content=None,
        image_content_type=None,
    )

    result = use_case.execute(input_dto)

    assert result.user_id == input_dto.user_id
    assert result.sex == input_dto.sex
    assert result.birthdate == input_dto.birthdate
    assert result.height_cm == input_dto.height_cm
    assert result.weight_kg == input_dto.weight_kg
    assert result.image_id is None

    # リポジトリにも保存されていることを確認
    stored = repo.get_by_user_id(UserId(result.user_id))
    assert stored is not None
    assert stored.height_cm.value == input_dto.height_cm
    assert stored.weight_kg.value == input_dto.weight_kg


def test_upsert_profile_updates_existing_profile_without_image_change() -> None:
    repo = InMemoryProfileRepository()
    use_case = _make_use_case(repo)

    user_id = "22222222-2222-2222-2222-222222222222"

    # まず初期プロフィールを作成
    input1 = UpsertProfileInputDTO(
        user_id=user_id,
        sex=Sex.FEMALE,
        birthdate=date(1985, 5, 10),
        height_cm=160.0,
        weight_kg=55.0,
    )
    result1 = use_case.execute(input1)

    # 次に身長・体重だけ変更して upsert（画像はなし）
    input2 = UpsertProfileInputDTO(
        user_id=user_id,
        sex=Sex.FEMALE,
        birthdate=date(1985, 5, 10),
        height_cm=161.0,
        weight_kg=56.0,
    )
    result2 = use_case.execute(input2)

    assert result2.user_id == result1.user_id
    assert result2.height_cm == 161.0
    assert result2.weight_kg == 56.0
    # 画像はどちらも None のまま
    assert result1.image_id is None
    assert result2.image_id is None

    stored = repo.get_by_user_id(UserId(user_id))
    assert stored is not None
    assert stored.height_cm.value == 161.0
    assert stored.weight_kg.value == 56.0


def test_upsert_profile_saves_image_when_provided() -> None:
    repo = InMemoryProfileRepository()
    use_case = _make_use_case(repo)

    user_id = "33333333-3333-3333-3333-333333333333"

    image_bytes = b"fake-image-binary"
    image_content_type = "image/png"

    input_dto = UpsertProfileInputDTO(
        user_id=user_id,
        sex=Sex.OTHER,
        birthdate=date(2000, 1, 1),
        height_cm=170.0,
        weight_kg=60.0,
        image_content=image_bytes,
        image_content_type=image_content_type,
    )

    result = use_case.execute(input_dto)

    assert result.user_id == user_id
    # InMemoryProfileImageStorage は保存時に image_id を必ず付与する
    assert result.image_id is not None

    stored = repo.get_by_user_id(UserId(user_id))
    assert stored is not None
    assert stored.image_id is not None
