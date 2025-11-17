#!/usr/bin/env sh
set -eu

# リポジトリルートから実行する前提
BACKEND_DIR="backend"
APP_DIR="$BACKEND_DIR/app"
TESTS_DIR="$BACKEND_DIR/tests"

echo "Backend dir: $BACKEND_DIR"
echo "App dir    : $APP_DIR"
echo "Tests dir  : $TESTS_DIR"

#----------------------------------------
# 1. ディレクトリ作成
#----------------------------------------
DIRS="
$BACKEND_DIR
$APP_DIR

$APP_DIR/domain
$APP_DIR/domain/auth
$APP_DIR/domain/common

$APP_DIR/application
$APP_DIR/application/auth
$APP_DIR/application/auth/ports
$APP_DIR/application/auth/dto
$APP_DIR/application/auth/use_cases
$APP_DIR/application/auth/use_cases/account
$APP_DIR/application/auth/use_cases/session
$APP_DIR/application/auth/use_cases/current_user

$APP_DIR/api
$APP_DIR/api/http
$APP_DIR/api/http/routers
$APP_DIR/api/http/dependencies
$APP_DIR/api/http/schemas

$APP_DIR/infra
$APP_DIR/infra/db
$APP_DIR/infra/db/models
$APP_DIR/infra/db/repositories
$APP_DIR/infra/db/migrations
$APP_DIR/infra/security
$APP_DIR/infra/time

$APP_DIR/di

$TESTS_DIR
$TESTS_DIR/application
$TESTS_DIR/application/auth
"

for dir in $DIRS; do
  if [ -n "$dir" ]; then
    if [ ! -d "$dir" ]; then
      mkdir -p "$dir"
      echo "Created dir : $dir"
    else
      echo "Skip dir    : $dir (already exists)"
    fi
  fi
done

#----------------------------------------
# 2. ファイル作成用の関数
#    - 既存なら何もしない
#----------------------------------------
create_file_if_missing() {
  path="$1"
  content="${2:-}"
  if [ -e "$path" ]; then
    echo "Skip file   : $path (already exists)"
  else
    # 念のためディレクトリを作成
    dirpath=$(dirname "$path")
    if [ ! -d "$dirpath" ]; then
      mkdir -p "$dirpath"
      echo "Created dir : $dirpath"
    fi
    printf "%s\n" "$content" > "$path"
    echo "Created file: $path"
  fi
}

#----------------------------------------
# 3. __init__.py 系（パッケージ用）
#----------------------------------------
INIT_FILES="
$APP_DIR/__init__.py
$APP_DIR/domain/__init__.py
$APP_DIR/domain/auth/__init__.py
$APP_DIR/domain/common/__init__.py

$APP_DIR/application/__init__.py
$APP_DIR/application/auth/__init__.py
$APP_DIR/application/auth/ports/__init__.py
$APP_DIR/application/auth/dto/__init__.py
$APP_DIR/application/auth/use_cases/__init__.py
$APP_DIR/application/auth/use_cases/account/__init__.py
$APP_DIR/application/auth/use_cases/session/__init__.py
$APP_DIR/application/auth/use_cases/current_user/__init__.py

$APP_DIR/api/__init__.py
$APP_DIR/api/http/__init__.py
$APP_DIR/api/http/routers/__init__.py
$APP_DIR/api/http/dependencies/__init__.py
$APP_DIR/api/http/schemas/__init__.py

$APP_DIR/infra/__init__.py
$APP_DIR/infra/db/__init__.py
$APP_DIR/infra/db/models/__init__.py
$APP_DIR/infra/db/repositories/__init__.py
$APP_DIR/infra/security/__init__.py
$APP_DIR/infra/time/__init__.py

$APP_DIR/di/__init__.py

$TESTS_DIR/__init__.py
$TESTS_DIR/application/__init__.py
$TESTS_DIR/application/auth/__init__.py
"

for f in $INIT_FILES; do
  if [ -n "$f" ]; then
    create_file_if_missing "$f" '"""Package."""'
  fi
done

#----------------------------------------
# 4. 「最低限、空で作っておきたい」ファイル群
#    （中身は軽いコメントだけ）
#----------------------------------------

# --- domain/auth ---
create_file_if_missing "$APP_DIR/domain/auth/entities.py" \
'"""Domain entities for auth (User, EmailAddress, HashedPassword, etc.)."""'

create_file_if_missing "$APP_DIR/domain/auth/value_objects.py" \
'"""Value objects for auth (Email, HashedPassword, etc.)."""'

# --- application/auth/ports ---
create_file_if_missing "$APP_DIR/application/auth/ports/user_repository_port.py" \
'"""Port for User repository."""'

create_file_if_missing "$APP_DIR/application/auth/ports/password_hasher_port.py" \
'"""Port for password hasher service."""'

create_file_if_missing "$APP_DIR/application/auth/ports/token_service_port.py" \
'"""Port for token service (JWT, etc.)."""'

create_file_if_missing "$APP_DIR/application/auth/ports/clock_port.py" \
'"""Port for clock abstraction (current time)."""'

# --- application/auth/dto ---
create_file_if_missing "$APP_DIR/application/auth/dto/register_dto.py" \
'"""DTOs for user registration use case."""'

create_file_if_missing "$APP_DIR/application/auth/dto/login_dto.py" \
'"""DTOs for user login use case."""'

create_file_if_missing "$APP_DIR/application/auth/dto/auth_user_dto.py" \
'"""Common DTO for authenticated user."""'

# --- use_cases ---
create_file_if_missing "$APP_DIR/application/auth/use_cases/account/register_user.py" \
'"""Use case: register user."""'

create_file_if_missing "$APP_DIR/application/auth/use_cases/session/login_user.py" \
'"""Use case: login user (create session)."""'

create_file_if_missing "$APP_DIR/application/auth/use_cases/current_user/get_current_user.py" \
'"""Use case: get current authenticated user."""'

# --- API / http ---
create_file_if_missing "$APP_DIR/api/http/routers/auth.py" \
'"""FastAPI router for /auth endpoints."""'

create_file_if_missing "$APP_DIR/api/http/schemas/auth.py" \
'"""Pydantic models for auth API (request/response)."""'

create_file_if_missing "$APP_DIR/api/http/dependencies/auth.py" \
'"""Auth-related dependencies (get_current_user, etc.)."""'

# --- infra / db ---
create_file_if_missing "$APP_DIR/infra/db/base.py" \
'"""SQLAlchemy Base and session factory will be defined here."""'

create_file_if_missing "$APP_DIR/infra/db/models/user.py" \
'"""SQLAlchemy model for User table."""'

create_file_if_missing "$APP_DIR/infra/db/repositories/user_repository.py" \
'"""UserRepositoryPort implementation using the database."""'

# --- infra / security ---
create_file_if_missing "$APP_DIR/infra/security/password_hasher.py" \
'"""PasswordHasherPort implementation (e.g., using passlib/bcrypt)."""'

create_file_if_missing "$APP_DIR/infra/security/jwt_token_service.py" \
'"""TokenServicePort implementation using JWT."""'

# --- infra / time ---
create_file_if_missing "$APP_DIR/infra/time/system_clock.py" \
'"""System clock implementation of ClockPort."""'

# --- DI ---
create_file_if_missing "$APP_DIR/di/container.py" \
'"""DI container wiring ports to concrete infra implementations."""'

# --- FastAPI entrypoint ---
create_file_if_missing "$APP_DIR/main.py" \
'"""FastAPI application entrypoint."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}
'

echo "Done. Backend structure initialized."
