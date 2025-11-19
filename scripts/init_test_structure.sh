#!/usr/bin/env bash
set -euo pipefail

# このスクリプトファイルの場所からリポジトリルートを計算
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "Project root: ${ROOT_DIR}"

# 作成したいディレクトリ一覧
DIRS=(
  "backend/tests"
  "backend/tests/unit"
  "backend/tests/unit/domain"
  "backend/tests/unit/domain/auth"
  "backend/tests/unit/application"
  "backend/tests/unit/application/auth"
  "backend/tests/unit/application/auth/use_cases"
)

# 作成したいファイル一覧
FILES=(
  "backend/tests/unit/domain/auth/test_value_objects.py"
  "backend/tests/unit/domain/auth/test_user_entity.py"
  "backend/tests/unit/application/auth/use_cases/test_register_user.py"
  "backend/tests/unit/application/auth/use_cases/test_login_user.py"
  "backend/tests/unit/application/auth/use_cases/test_get_current_user.py"
  "backend/tests/conftest.py"
  "backend/tests/__init__.py"
)

echo "=== Create directories (skip if exists) ==="
for rel_dir in "${DIRS[@]}"; do
  dir_path="${ROOT_DIR}/${rel_dir}"
  if [ -d "${dir_path}" ]; then
    echo "skip dir (already exists): ${rel_dir}"
  else
    echo "create dir: ${rel_dir}"
    mkdir -p "${dir_path}"
  fi
done

echo "=== Create files (skip if exists) ==="
for rel_file in "${FILES[@]}"; do
  file_path="${ROOT_DIR}/${rel_file}"
  if [ -e "${file_path}" ]; then
    echo "skip file (already exists): ${rel_file}"
  else
    echo "create file: ${rel_file}"
    # 中身は空（もしくは最低限のコメント）でOKならこれで十分
    echo "# TODO: add tests for ${rel_file}" > "${file_path}"
  fi
done

echo "Done."
