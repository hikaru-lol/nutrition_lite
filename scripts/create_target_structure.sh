#!/usr/bin/env bash
set -euo pipefail

# このスクリプトは `script/` ディレクトリ内に置かれている前提
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
APP_DIR="${BACKEND_DIR}/app"

if [ ! -d "${BACKEND_DIR}" ]; then
  echo "バックエンドディレクトリが見つかりません: ${BACKEND_DIR}"
  echo "backend/ と script/ が同じ階層にあることを確認してください。"
  exit 1
fi

echo "PROJECT_ROOT: ${PROJECT_ROOT}"
echo "BACKEND_DIR : ${BACKEND_DIR}"
echo "APP_DIR     : ${APP_DIR}"
echo

create_dir() {
  local dir="$1"
  if [ -d "${dir}" ]; then
    echo "skip dir (exists): ${dir}"
  else
    echo "create dir       : ${dir}"
    mkdir -p "${dir}"
  fi
}

create_file() {
  local file="$1"
  if [ -f "${file}" ]; then
    echo "skip file (exists): ${file}"
  else
    echo "create file        : ${file}"
    # 空ファイルを作成（必要ならここでテンプレートを書き込んでもOK）
    : > "${file}"
  fi
}

# ---------- ディレクトリ作成 ----------

DIRS=(
  # domain
  "${APP_DIR}/domain/target"

  # application
  "${APP_DIR}/application/target"
  "${APP_DIR}/application/target/dto"
  "${APP_DIR}/application/target/ports"
  "${APP_DIR}/application/target/use_cases"

  # infra
  "${APP_DIR}/infra/db/models"
  "${APP_DIR}/infra/db/repositories"
  "${APP_DIR}/infra/llm"

  # api
  "${APP_DIR}/api/http/schemas"
  "${APP_DIR}/api/http/routers"
)

for d in "${DIRS[@]}"; do
  create_dir "${d}"
done

echo

# ---------- ファイル作成 ----------

FILES=(
  # domain/target
  "${APP_DIR}/domain/target/__init__.py"
  "${APP_DIR}/domain/target/entities.py"
  "${APP_DIR}/domain/target/value_objects.py"

  # application/target
  "${APP_DIR}/application/target/__init__.py"

  # application/target/dto
  "${APP_DIR}/application/target/dto/__init__.py"
  "${APP_DIR}/application/target/dto/target_dto.py"

  # application/target/ports
  "${APP_DIR}/application/target/ports/__init__.py"
  "${APP_DIR}/application/target/ports/target_repository_port.py"
  "${APP_DIR}/application/target/ports/target_snapshot_repository_port.py"
  "${APP_DIR}/application/target/ports/target_generator_port.py"
  "${APP_DIR}/application/target/ports/uow_port.py"

  # application/target/use_cases
  "${APP_DIR}/application/target/use_cases/__init__.py"
  "${APP_DIR}/application/target/use_cases/create_target.py"
  "${APP_DIR}/application/target/use_cases/get_active_target.py"
  "${APP_DIR}/application/target/use_cases/list_targets.py"
  "${APP_DIR}/application/target/use_cases/activate_target.py"
  "${APP_DIR}/application/target/use_cases/update_target.py"
  "${APP_DIR}/application/target/use_cases/ensure_daily_snapshot.py"

  # infra/db
  "${APP_DIR}/infra/db/models/target.py"
  "${APP_DIR}/infra/db/repositories/target_repository.py"
  "${APP_DIR}/infra/db/repositories/target_snapshot_repository.py"

  # infra/llm
  "${APP_DIR}/infra/llm/target_generator_stub.py"

  # api/http
  "${APP_DIR}/api/http/schemas/target.py"
  "${APP_DIR}/api/http/routers/target_route.py"
)

for f in "${FILES[@]}"; do
  create_file "${f}"
done

echo
echo "✅ target 関連のディレクトリ・ファイル作成が完了しました。"
