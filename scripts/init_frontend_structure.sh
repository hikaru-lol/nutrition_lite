#!/usr/bin/env bash
set -euo pipefail

# このスクリプトが置かれているディレクトリ
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# プロジェクトのルート（= script/ の一つ上）
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ==============================
# 作成したいディレクトリ一覧
# ==============================
DIRS=(
  # project root
  "backend"
  "frontend"
  "docs"

  # frontend base
  "frontend/public"
  "frontend/app"
  "frontend/components"
  "frontend/lib"
  "frontend/styles"
  "frontend/types"

  # app route groups
  "frontend/app/(public)"
  "frontend/app/(public)/auth"
  "frontend/app/(public)/auth/login"
  "frontend/app/(public)/auth/register"

  "frontend/app/(onboarding)"
  "frontend/app/(onboarding)/onboarding"
  "frontend/app/(onboarding)/onboarding/profile"
  "frontend/app/(onboarding)/onboarding/target"

  "frontend/app/(app)"
  "frontend/app/(app)/meals"
  "frontend/app/(app)/reports"
  "frontend/app/(app)/reports/daily"
  "frontend/app/(app)/reports/daily/[date]"
  "frontend/app/(app)/targets"
  "frontend/app/(app)/recommendations"
  "frontend/app/(app)/recommendations/today"
  "frontend/app/(app)/billing"
  "frontend/app/(app)/billing/upgrade"
  "frontend/app/(app)/billing/plan"
  "frontend/app/(app)/profile"

  # components
  "frontend/components/ui"
  "frontend/components/layout"
  "frontend/components/auth"
  "frontend/components/profile"
  "frontend/components/today"
  "frontend/components/meals"
  "frontend/components/reports"
  "frontend/components/common"
  "frontend/components/targets"

  # lib
  "frontend/lib/api"
  "frontend/lib/hooks"
)

# ==============================
# 作成したいファイル一覧
# ==============================
FILES=(
  # docs
  "docs/frontend_business_requirements.md"
  "docs/frontend_screen_map.md"
  "docs/frontend_components.md"

  # frontend root configs
  "frontend/package.json"
  "frontend/tsconfig.json"
  "frontend/next.config.mjs"
  "frontend/postcss.config.cjs"
  "frontend/tailwind.config.cjs"
  "frontend/.eslintrc.cjs"

  # public
  "frontend/public/favicon.ico"

  # app root
  "frontend/app/layout.tsx"
  "frontend/app/globals.css"                 # app/直下に置くパターン用（不要なら削除OK）

  # (public)/auth
  "frontend/app/(public)/auth/layout.tsx"
  "frontend/app/(public)/auth/login/page.tsx"
  "frontend/app/(public)/auth/register/page.tsx"

  # (onboarding)
  "frontend/app/(onboarding)/onboarding/layout.tsx"
  "frontend/app/(onboarding)/onboarding/profile/page.tsx"
  "frontend/app/(onboarding)/onboarding/target/page.tsx"

  # (app)
  "frontend/app/(app)/layout.tsx"
  "frontend/app/(app)/page.tsx"
  "frontend/app/(app)/meals/page.tsx"
  "frontend/app/(app)/reports/daily/[date]/page.tsx"
  "frontend/app/(app)/targets/page.tsx"
  "frontend/app/(app)/recommendations/today/page.tsx"
  "frontend/app/(app)/billing/upgrade/page.tsx"
  "frontend/app/(app)/billing/plan/page.tsx"
  "frontend/app/(app)/profile/page.tsx"

  # components/ui
  "frontend/components/ui/button.tsx"
  "frontend/components/ui/card.tsx"
  "frontend/components/ui/input.tsx"
  "frontend/components/ui/label.tsx"
  "frontend/components/ui/badge.tsx"

  # components/layout
  "frontend/components/layout/AppShell.tsx"
  "frontend/components/layout/AppHeader.tsx"
  "frontend/components/layout/AppSidebar.tsx"
  "frontend/components/layout/NavLink.tsx"
  "frontend/components/layout/PageHeader.tsx"

  # components/auth
  "frontend/components/auth/AuthCard.tsx"
  "frontend/components/auth/LoginForm.tsx"
  "frontend/components/auth/RegisterForm.tsx"

  # components/profile
  "frontend/components/profile/ProfileForm.tsx"

  # components/today
  "frontend/components/today/TodayPage.tsx"
  "frontend/components/today/TodayHeader.tsx"
  "frontend/components/today/TodayProgressCard.tsx"
  "frontend/components/today/TodayMealsSummaryCard.tsx"
  "frontend/components/today/TodayReportPreviewCard.tsx"
  "frontend/components/today/TodayRecommendationPreviewCard.tsx"

  # components/meals
  "frontend/components/meals/MealsPage.tsx"
  "frontend/components/meals/MealsHeader.tsx"
  "frontend/components/meals/MainMealsSection.tsx"
  "frontend/components/meals/MealSlotCard.tsx"
  "frontend/components/meals/MealItemList.tsx"
  "frontend/components/meals/MealItemRow.tsx"
  "frontend/components/meals/SnackMealsSection.tsx"
  "frontend/components/meals/MealItemDialog.tsx"

  # components/reports
  "frontend/components/reports/DailyReportPage.tsx"
  "frontend/components/reports/DailyReportHeader.tsx"
  "frontend/components/reports/DailyReportCard.tsx"
  "frontend/components/reports/ReportSection.tsx"
  "frontend/components/reports/ReportActions.tsx"

  # components/common
  "frontend/components/common/UpgradeBanner.tsx"

  # components/targets
  "frontend/components/targets/TargetsPage.tsx"
  "frontend/components/targets/TargetList.tsx"
  "frontend/components/targets/TargetCard.tsx"
  "frontend/components/targets/CreateTargetDialog.tsx"

  # lib/api
  "frontend/lib/api/client.ts"
  "frontend/lib/api/auth.ts"
  "frontend/lib/api/profile.ts"
  "frontend/lib/api/meals.ts"
  "frontend/lib/api/dailyReport.ts"
  "frontend/lib/api/today.ts"
  "frontend/lib/api/billing.ts"

  # lib/hooks
  "frontend/lib/hooks/useCurrentUser.ts"
  "frontend/lib/hooks/useTodayOverview.ts"
  "frontend/lib/hooks/useMealsByDate.ts"
  "frontend/lib/hooks/useDailyReport.ts"

  # lib/utils
  "frontend/lib/utils.ts"

  # styles
  "frontend/styles/globals.css"             # styles/配下に置くパターン用

  # types
  "frontend/types/auth.ts"
  "frontend/types/profile.ts"
  "frontend/types/meal.ts"
  "frontend/types/nutrition.ts"
  "frontend/types/report.ts"
  "frontend/types/target.ts"
)

echo "=== Create directories ==="
for dir in "${DIRS[@]}"; do
  TARGET="${ROOT_DIR}/${dir}"
  if [ -d "$TARGET" ]; then
    echo "SKIP (dir exists): $dir"
  else
    mkdir -p "$TARGET"
    echo "CREATE dir: $dir"
  fi
done

echo
echo "=== Create files ==="
for file in "${FILES[@]}"; do
  TARGET="${ROOT_DIR}/${file}"
  if [ -e "$TARGET" ]; then
    echo "SKIP (file exists): $file"
  else
    mkdir -p "$(dirname "$TARGET")"
    touch "$TARGET"
    echo "CREATE file: $file"
  fi
done

echo
echo "Done ✅"
