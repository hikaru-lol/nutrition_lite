いいですね、じゃあ auth だけにフォーカスして、プロフィールと同じノリで

ざっくり仕様
外部仕様（API / UX）
内部仕様（ドメイン / UseCase / Repo / セキュリティ）
を整理していきます 💪

Auth 機能の仕様 0. 概要
目的

ユーザーのアカウント管理（登録 / 認証 / 退会）
セッション管理（JWT + HttpOnly Cookie）
プラン情報（TRIAL / FREE / PAID）と試用期間の管理の「入口」
Auth 自体は「ログインできる状態」を作るのが責務で、
課金やプラン遷移の詳細は Billing モジュールと連携する前提。

1. Auth のデータ仕様（ドメイン）
   1-1. User エンティティ
   ※ 型はイメージ。実際はすでにある User 定義に合わせる前提。

User(
id: UserId, # UUID 文字列の VO
email: EmailAddress,
hashed_password: HashedPassword,
name: str,
plan: UserPlan, # TRIAL / FREE / PAID
trial_info: TrialInfo, # trial_ends_at を含む
has_profile: bool, # プロフィールを作成済みか
created_at: datetime,
deleted_at: datetime | None,
)
1-2. 値オブジェクト / Enum
UserId（str ラッパ）

空文字は不可
EmailAddress

メール形式バリデーション
不正なら InvalidEmailFormatError
HashedPassword

生パスワードではなく、「ハッシュ済みであること」を意味する VO
UserPlan: StrEnum

TRIAL = "trial"
FREE = "free"
PAID = "paid"
TrialInfo

trial_ends_at: datetime | None
is_trial_active: bool（now < trial_ends_at なら True）
1-3. ドメイン上の制約
email は全ユーザーで一意（ユニーク制約）

deleted_at is not None なユーザーは ログイン不可

新規ユーザーは必ず UserPlan = TRIAL + trial_ends_at = created_at + 7 日

trial_ends_at を超えたら、

Billing 側の状態に応じて FREE or PAID に切り替え 2. 外部仕様（API / UX 視点）
2-1. 利用者と前提
操作主体：未ログインユーザー（Register/Login）、ログイン済みユーザー（Me/Logout/Delete）

セッションは「JWT + HttpOnly Cookie」で管理：

ACCESS_TOKEN（短命、例：15〜30 分）
REFRESH_TOKEN（長め、例：7〜30 日）
Cookie 設定例：

HttpOnly = True
Secure = 本番のみ True
SameSite = "lax" or "none"（設定で切り替え）
2-2. エンドポイント一覧（外部仕様）
(1) POST /auth/register
目的：新規ユーザー登録 + ログイン状態にする
リクエストボディ例：
{
"email": "user@example.com",
"password": "PlainPassword123",
"name": "Hikaru"
}
振る舞い：

email フォーマットチェック

email 重複チェック（既に存在 → 409 / EmailAlreadyUsedError）

パスワードハッシュ

User 作成：

plan = TRIAL
trial_ends_at = now + 7 days
has_profile = false
ACCESS_TOKEN / REFRESH_TOKEN を発行し、HttpOnly Cookie にセット

レスポンス：

201 Created + シンプルなユーザー情報（id, email, plan, trial_ends_at など）
(2) POST /auth/login
目的：既存ユーザーのログイン
リクエスト：
{
"email": "user@example.com",
"password": "PlainPassword123"
}
振る舞い：

email でユーザー取得（なければ 401）
パスワード検証（不一致なら 401）
deleted_at が設定されていれば 401
ACCESS_TOKEN / REFRESH_TOKEN を再発行し Cookie にセット
レスポンス：

200 OK + 現在のユーザー情報（plan, trial_ends_at, has_profile など）
(3) POST /auth/refresh
目的：Refresh Token から新しい Access Token を取得

入力：

Cookie の REFRESH_TOKEN（ヘッダには何も不要）
振る舞い：

REFRESH_TOKEN を検証（署名・期限・形式）
トークン内の user_id を元にユーザー取得
deleted_at がある場合は 401
新しい ACCESS_TOKEN（必要なら REFRESH_TOKEN も）を発行し Cookie 再セット
レスポンス：

200 OK + {"ok": true} 的な軽い情報、もしくは現在ユーザー情報
(4) POST /auth/logout
目的：ログアウト（クライアントセッションの終了）

入力：

Cookie（ACCESS_TOKEN / REFRESH_TOKEN）
振る舞い：

両方の Cookie を「無効値 + 即時 expire」で上書き
サーバー側で Refresh Token の失効を管理する場合はここで無効化登録
レスポンス：

204 No Content
(5) GET /auth/me
目的：現在ログイン中のユーザー情報を取得

認証：

ACCESS_TOKEN Cookie を使用。
無効・期限切れ → 401。
レスポンス例：

{
"id": "user-uuid",
"email": "user@example.com",
"name": "Hikaru",
"plan": "trial",
"trial_ends_at": "2025-01-10T12:34:56Z",
"has_profile": true
}
(6) DELETE /auth/me
目的：アカウント削除（退会）

認証：

ログイン済み
振る舞い：

User の deleted_at をセット（ソフトデリート）
関連データは即時削除 or 後続ジョブで削除（方針次第）
Cookie の ACCESS/REFRESH を失効
レスポンス：

204 No Content
2-3. プラン・試用期間の外部的ふるまい
/auth/me で返す情報に：

plan
trial_ends_at
is_trial_active（あっても良い）
フロント側はこの情報を使って：

「残り何日 TRIAL か」
「TRIAL 終了後は課金 or FREE になるか」
などを表示。
課金に関する実際の購読状態・Stripe ID などは Billing モジュール側 で持つ
（auth は「論理プラン値」のみ管理）。

3. 内部仕様（ドメイン / UseCase / Repo / セキュリティ）
   3-1. Domain: User とエラー
   User エンティティは前述のフィールドをもつ。

主なドメインエラー：

InvalidEmailFormatError
EmailAlreadyUsedError
InvalidUserPlanError（必要なら）
3-2. Application Ports
UserRepositoryPort
class UserRepositoryPort(Protocol):
def get_by_email(self, email: EmailAddress) -> User | None: ...
def get_by_id(self, user_id: UserId) -> User | None: ...
def save(self, user: User) -> None: ...
PasswordHasherPort
class PasswordHasherPort(Protocol):
def hash(self, raw_password: str) -> HashedPassword: ...
def verify(self, raw_password: str, hashed: HashedPassword) -> bool: ...
TokenServicePort
class TokenServicePort(Protocol):
def create_access_token(self, payload: TokenPayload) -> str: ...
def create_refresh_token(self, payload: TokenPayload) -> str: ...
def verify_refresh_token(self, token: str) -> TokenPayload: ...
TokenPayload：

user_id: str
plan: str など（最低限 user_id）
ClockPort
class ClockPort(Protocol):
def now(self) -> datetime: ...
3-3. UseCase 一覧
RegisterUserUseCase
LoginUserUseCase
RefreshTokenUseCase
LogoutUserUseCase
GetCurrentUserUseCase（/auth/me 用）
DeleteUserUseCase（/auth/me DELETE）
3-4. 各 UseCase の内部仕様（ざっくり）
RegisterUserUseCase
入力：email, password, name

流れ：

EmailAddress VO 生成（フォーマットチェック）
UserRepository で get_by_email → 既に存在すれば EmailAlreadyUsedError
PasswordHasher でハッシュ生成
UserPlan.TRIAL + TrialInfo(trial_ends_at = clock.now() + 7 日) で User 作成
Repo.save
TokenService で ACCESS / REFRESH 作成（payload に user_id 等）
DTO 経由でユーザー情報とトークン（または Cookie セットを API 層に委譲）を返す
LoginUserUseCase
入力：email, password

流れ：

EmailAddress からユーザー検索
ユーザーなし or deleted_at あり → 認証失敗
PasswordHasher.verify で検証
TokenService で ACCESS / REFRESH 再発行
ユーザー情報とトークン情報を DTO で返す
RefreshTokenUseCase
入力：refresh_token

流れ：

TokenService.verify_refresh_token → TokenPayload 取得
添付された user_id をもとに UserRepo からユーザー取得
deleted_at があれば 401
TokenService.create_access_token で新しい ACCESS_TOKEN を発行
必要なら REFRESH_TOKEN もローテーション（セキュリティポリシー次第）
LogoutUserUseCase
入力：user_id（実質使わないことも多い）

流れ：

基本的には Stateless なので、サーバー側では特に何もしない
Blacklist やセッションレコードがある場合はそこで無効化
API 層に「Cookie クリアしてね」というシグナルを返す程度
GetCurrentUserUseCase
入力：user_id（ACCESS_TOKEN から抽出）

流れ：

UserRepo.get_by_id
ユーザーが存在し、deleted_at がないことを確認
ユーザー情報を DTO で返す
DeleteUserUseCase
入力：user_id

流れ：

UserRepo.get_by_id

見つからなければ 404 or 無視（ポリシー次第）

deleted_at = now でソフトデリート

関連データ削除は：

すぐに消す or 別ジョブで削除（後で設計）
3-5. セキュリティ仕様（最低限）
パスワードは必ずハッシュ化（bcrypt 等）

JWT 署名には十分な長さのランダムシークレットキー（環境変数から）

Cookie 設定：

本番：

Secure = True
SameSite = "none" or "lax"（フロントとの構成による）
開発：

Secure = False
SameSite = "lax"
トークンの有効期限：

ACCESS_TOKEN：短め（15〜30 分）
REFRESH_TOKEN：長め（7〜30 日）
重要：

課金・プランチェックは auth ではなく「アプリケーション層の UC 側」で行う
（例：栄養計算の UC が「このユーザーの plan が TRIAL/PAID か？」をチェック） 4. まとめ（Auth の仕様のポイント）
外部仕様（ユーザー視点）

email + password + name で登録 → 7 日間の TRIAL 開始 → 即ログイン状態
ログイン・ログアウト・セッション継続（Refresh）・退会ができる
/auth/me で自分のプランや試用期間の情報が取れる
内部仕様（システム視点）

Domain: User / UserPlan / TrialInfo / EmailAddress / UserId で「ユーザーと状態」を表現
Application: Register / Login / Refresh / Logout / Me / Delete の UC が責務を明確化
Infra: UserRepository / PasswordHasher / TokenService / Clock の実装を DI で差し込む
Billing と連動するのは「プランの更新」だけで、
Auth 自体は「誰がどのプランでログインしているか」を表現するモジュール
こんな形で Auth の仕様を固めておけば、
このあと Billing や「プラン別制限」「栄養計算 UC のガードロジック」を乗せていくときもズレずに進められるはずです 💡
