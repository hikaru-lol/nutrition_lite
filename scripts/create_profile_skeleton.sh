#!/usr/bin/env bash
set -euo pipefail

# このスクリプト自身が置かれているディレクトリ（= repo-root/script）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="${SCRIPT_DIR}/../backend"

if [ ! -d "${BACKEND_ROOT}" ]; then
  echo "ERROR: backend ディレクトリが見つかりません: ${BACKEND_ROOT}" >&2
  exit 1
fi

echo "Backend root: ${BACKEND_ROOT}"

########################################
# 1) app/domain/profile
########################################

FILE="${BACKEND_ROOT}/app/domain/profile/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Profile domain package."""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/domain/profile/entities.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Domain entities for user profiles.

ここには Profile エンティティを定義していく予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/domain/profile/value_objects.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Value objects for user profiles.

Sex, HeightCm, WeightKg, ProfileImageId などを定義予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

########################################
# 2) app/application/profile
########################################

FILE="${BACKEND_ROOT}/app/application/profile/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Application layer for profile domain."""
EOF
  echo "[CREATE] $FILE"
fi

# dto
FILE="${BACKEND_ROOT}/app/application/profile/dto/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""DTOs for profile use cases."""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/dto/profile_dto.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Data Transfer Objects for profile use cases.

ProfileDTO, UpsertProfileInputDTO などを定義予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

# ports
FILE="${BACKEND_ROOT}/app/application/profile/ports/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Ports (interfaces) for profile domain.

ProfileRepositoryPort, ProfileImageStoragePort, ProfileUnitOfWorkPort などを定義予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/ports/profile_repository_port.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""ProfileRepositoryPort - 永続化用のポート。"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/ports/profile_image_storage_port.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""ProfileImageStoragePort - プロフィール画像ストレージ用のポート。"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/ports/uow_port.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""ProfileUnitOfWorkPort - profile 用の Unit of Work ポート。"""
EOF
  echo "[CREATE] $FILE"
fi

# use_cases
FILE="${BACKEND_ROOT}/app/application/profile/use_cases/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Use cases for profile domain."""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/use_cases/upsert_profile.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""UpsertProfileUseCase - プロフィールの作成/更新用ユースケース。"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/application/profile/use_cases/get_my_profile.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""GetMyProfileUseCase - 現在ユーザーのプロフィール取得用ユースケース。"""
EOF
  echo "[CREATE] $FILE"
fi

########################################
# 3) infra/db（profile 用）
########################################

FILE="${BACKEND_ROOT}/app/infra/db/models/profile.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""SQLAlchemy model for Profile.

ProfileModel をここに定義する予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/infra/db/repositories/profile_repository.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""SqlAlchemyProfileRepository - ProfileRepositoryPort の実装。"""
EOF
  echo "[CREATE] $FILE"
fi

########################################
# 4) infra/storage（プロフィール画像）
########################################

FILE="${BACKEND_ROOT}/app/infra/storage/__init__.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Storage-related adapters (e.g., profile images)."""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/infra/storage/profile_image_storage.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""ProfileImageStorage adapter implementations.

InMemoryProfileImageStorage や MinIO/S3 向けの実装をここに追加していく予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

########################################
# 5) api/http（profile 用 HTTP インターフェイス）
########################################

FILE="${BACKEND_ROOT}/app/api/http/schemas/profile.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""Pydantic schemas for profile HTTP API.

ProfileRequest / ProfileResponse などを定義予定。
"""
EOF
  echo "[CREATE] $FILE"
fi

FILE="${BACKEND_ROOT}/app/api/http/routers/profile_route.py"
if [ -e "$FILE" ]; then
  echo "[SKIP] $FILE (already exists)"
else
  mkdir -p "$(dirname "$FILE")"
  cat << 'EOF' > "$FILE"
"""FastAPI router for profile endpoints.

GET /profile/me
PUT /profile/me
などをここに定義していく予定。
"""

from fastapi import APIRouter

router = APIRouter(prefix="/profile", tags=["Profile"])
EOF
  echo "[CREATE] $FILE"
fi

echo "Done."
