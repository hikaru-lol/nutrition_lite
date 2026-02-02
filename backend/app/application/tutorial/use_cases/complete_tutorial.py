"""チュートリアル完了ユースケース"""

from __future__ import annotations

from app.application.tutorial.dto.tutorial_dto import (
    CompleteTutorialInputDTO,
    CompleteTutorialOutputDTO,
)
from app.application.tutorial.ports.tutorial_unit_of_work_port import TutorialUnitOfWorkPort
from app.domain.tutorial.errors import TutorialAlreadyCompletedError
from app.domain.tutorial.services import validate_tutorial_id
from app.domain.tutorial.value_objects import TutorialCompletion, UserId


class CompleteTutorialUseCase:
    """チュートリアル完了ユースケース

    指定されたチュートリアルを完了済みとしてマークする
    """

    def __init__(self, tutorial_uow: TutorialUnitOfWorkPort):
        self._tutorial_uow = tutorial_uow

    def execute(self, input_dto: CompleteTutorialInputDTO) -> CompleteTutorialOutputDTO:
        """チュートリアルを完了としてマーク

        Args:
            input_dto: 入力DTO

        Returns:
            CompleteTutorialOutputDTO: 完了結果

        Raises:
            InvalidTutorialIdError: 無効なチュートリアルIDの場合
            TutorialAlreadyCompletedError: 既に完了済みの場合
        """
        user_id = UserId(input_dto.user_id)

        # チュートリアルID検証
        tutorial_id = validate_tutorial_id(input_dto.tutorial_id)

        # UoWパターンでトランザクション管理
        with self._tutorial_uow as uow:
            # 既に完了済みかチェック
            if uow.tutorial_repo.exists(user_id, tutorial_id):
                raise TutorialAlreadyCompletedError(
                    user_id=input_dto.user_id,
                    tutorial_id=input_dto.tutorial_id
                )

            # 完了記録を作成・保存
            completion = TutorialCompletion.create(user_id, tutorial_id)
            uow.tutorial_repo.add(completion)

        return CompleteTutorialOutputDTO(
            tutorial_id=completion.tutorial_id,
            completed_at=completion.completed_at,
        )