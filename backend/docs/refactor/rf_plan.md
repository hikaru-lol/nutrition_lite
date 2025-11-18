## 修正点、気になったところをまとめていく

パスワードのハッシュ化

DB の UOW の活用

refresh_token / logout / delete_account の UseCase 実装

/auth/refresh のエンドポイント追加

簡単な pytest（RegisterUserUseCase / LoginUserUseCase 単体テスト）

あたりを進めていくのが良さそうです。

API 契約

エラーの設計

ここから中身についてすこちリファクタリングを加えていく

軽い統合テストの追加：主に API で定義した契約通りのデータがりく、レスされるのかを確認する

リファクタリング１
UOW の追加
エラーの修正：かたに合わせる
