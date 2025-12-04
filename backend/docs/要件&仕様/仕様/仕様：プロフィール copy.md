了解！じゃあまずは プロフィール機能だけにフォーカスして、

もともとの仕様

外部仕様（API／UX 視点）

内部仕様（ドメイン／UseCase／Repo 視点）

をまとめていきます 💪

プロフィール機能の仕様 0. 概要
目的
ユーザーの基本情報（性別・身長・体重など）と、
アプリ動作の前提となる meals_per_day（1 日のメイン食事回数）を管理する。

この情報は以下に利用される：

ターゲット生成（LLM による 1 日分の栄養目標）

記録完了判定（DailyLogCompletion）

日次レポート・提案の前提情報

将来的なバッジ・分析など

1. プロフィールのデータ仕様
   1-1. 項目
   （ドメイン的な「意味」と「型」の定義）

項目 型 必須 説明
user_id UserId (str UUID) Yes このプロフィールの所有者
sex enum (male / female / other / unspecified) No 性別
birthdate date No 生年月日
height_cm float No 身長（cm）
weight_kg float No 体重（kg）
meals_per_day int Yes 1 日のメイン食事回数（1 以上）
image_id `str	None` No
created_at datetime Yes 作成日時
updated_at datetime Yes 更新日時
Repo 実装
SqlAlchemyProfileRepository(ProfileRepositoryPort)：

get_by_user_id：

user_id でフィルタ → Entity に変換

save：

既存モデルの有無をチェック → insert / update

画像ストレージ
ProfileImageStoragePort：

save(file: bytes) -> image_id: str

get_url(image_id: str) -> str

MinIO 実装 or ローカルストレージ実装

3-4. 他コンテキストとの関係
DailyLogCompletionUseCase：

ProfileRepo から Profile を取得 → meals_per_day がない/おかしい場合はエラー

GenerateDailyNutritionReportUseCase：

レポート生成前に Profile を取得し、LLM 入力に渡す

GenerateMealRecommendationUseCase：

提案生成時にも Profile を取得し、LLM 入力に渡す

4. まとめ（プロフィール機能の仕様のポイント）
   外部仕様（ユーザー視点）

自分のプロフィールを登録・更新・取得できる

meals_per_day を必ず設定する（記録完了・レポート・提案に必要）

プロフィール画像も設定可能

プロフィールがないと、栄養計算 / レポート / 提案は利用不可

内部仕様（システム視点）

Domain: Profile エンティティが「意味と制約」を持つ中心体

Application: Get / Upsert / UpdateImage の UseCase を通して操作

Infra: SQLAlchemy モデル + Repository + 画像ストレージアダプタ

他機能は ProfileRepositoryPort 経由で Profile を読み取り、
存在しない場合は明示的なエラーとして扱う

こんな感じでプロフィールを一段深く具体化しました。
次は同じノリで「ターゲット」「記録完了」「日次レポート」「提案」みたいに機能ごとに掘っていけますが、
どれからやりたいか順番決めちゃっても OK です（ターゲット or 記録完了あたりからが相性良さそう）。
