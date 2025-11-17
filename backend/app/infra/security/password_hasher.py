from __future__ import annotations

from passlib.context import CryptContext

from app.application.auth.ports.password_hasher_port import PasswordHasherPort
from app.domain.auth.value_objects import HashedPassword


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BcryptPasswordHasher(PasswordHasherPort):
    def hash(self, raw_password: str) -> HashedPassword:
        hashed = _pwd_context.hash(raw_password)
        return HashedPassword(hashed)

    def verify(self, raw_password: str, hashed_password: HashedPassword) -> bool:
        return _pwd_context.verify(raw_password, hashed_password.value)
