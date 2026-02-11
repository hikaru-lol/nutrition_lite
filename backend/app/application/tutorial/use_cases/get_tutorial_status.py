"""チュートリアル状況取得ユースケース"""

from __future__ import annotations

from app.application.tutorial.dto.tutorial_dto import (
    GetTutorialStatusInputDTO,
    GetTutorialStatusOutputDTO,
)
from app.application.tutorial.ports.tutorial_unit_of_work_port import TutorialUnitOfWorkPort
from app.domain.tutorial.value_objects import UserId


class GetTutorialStatusUseCase:
    """チュートリアル状況取得ユースケース

    ユーザーが完了済みのチュートリアル一覧を取得する
    """

    def __init__(self, tutorial_uow: TutorialUnitOfWorkPort):
        self._tutorial_uow = tutorial_uow

    def execute(self, input_dto: GetTutorialStatusInputDTO) -> GetTutorialStatusOutputDTO:
        """チュートリアル完了状況を取得

        Args:
            input_dto: 入力DTO

        Returns:
            GetTutorialStatusOutputDTO: 完了済みチュートリアルのリスト
        """
        user_id = UserId(input_dto.user_id)

        # UoWパターンでデータ取得
        with self._tutorial_uow as uow:
            # 完了済みチュートリアル一覧を取得
            completions = uow.tutorial_repo.list_completed_by_user(user_id)

        # チュートリアルIDのリストを抽出
        completed_tutorial_ids = [completion.tutorial_id for completion in completions]

        return GetTutorialStatusOutputDTO(
            completed_tutorial_ids=completed_tutorial_ids
        )