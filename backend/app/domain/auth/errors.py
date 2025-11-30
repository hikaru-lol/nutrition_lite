class AuthError(Exception):
    """
    認証・認可まわりの共通ベースエラー。

    - 認証失敗
    - ユーザー未検出
    - リフレッシュトークン不正
    など、Auth コンテキストで発生するアプリケーション / ドメインエラーの親クラス。
    """
    pass


class EmailAlreadyUsedError(AuthError):
    """既に登録済みのメールアドレスが使われたときのエラー。"""
    pass


class InvalidCredentialsError(AuthError):
    """メールアドレスまたはパスワードが不正なときのエラー。"""
    pass


class UserNotFoundError(AuthError):
    """指定されたユーザーが見つからないときのエラー。"""
    pass


class InvalidRefreshTokenError(AuthError):
    """リフレッシュトークンが不正 / 期限切れのときのエラー。"""
    pass


class InvalidEmailFormatError(AuthError):
    """メールアドレスの形式が不正なときのエラー。"""
    pass
