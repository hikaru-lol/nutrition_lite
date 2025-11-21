リファクタ

エラーの問題
バリューエラー問題
API 層で変換されていない

- ValueError を FastAPI で直接ハンドリング 1. app/api/http/errors.py に async def value*error_handler(*: Request, exc: ValueError) を追加し、validation_error_handler と同じフォーマットで 400/VALIDATION_ERROR を返すようにします。 2. app/main.py で app.add_exception_handler(ValueError, value_error_handler) を登録します。 3. これにより VO 起因の ValueError も API レイヤで {"error":{"code":"VALIDATION_ERROR","message":...}} に統一されます。

  - アプリ層で Domain エラーにマッピング
    1. VO を生成する箇所（例: register/login use case で EmailAddress を new するところ）を try/except ValueError で囲み、捕捉したら InvalidCredentialsError や新しいドメインエラー（例: InvalidUserInputError）にラップして再送出します。
    2. そのドメインエラーを app/domain/auth/errors.py に追加し、auth_error_handler に HTTP 400 への変換ロジックを記述します。
    3. API から見れば常に AuthError 経由で整形されたレスポンスになるので、下層の実装詳細（ValueError）を意識せずに済みます。
  - テスト面
    1. 統合テストに「VO が ValueError を投げるケース」（例: register/login で不正メール）を追加し、VALIDATION_ERROR が返ってくることを確認します。
    2. ユニットテストでも EmailAddress("bad") を引き起こすケースを追加し、use case が適切なドメインエラーを出すか、FastAPI handler が 400 を返すかを検証します。

  どちらか片方、もしくは両方組み合わせる形で、ValueError を 500 にしない流れを作れます。
