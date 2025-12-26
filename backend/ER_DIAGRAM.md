# データベース ER 図

## エンティティリレーションシップ図

```mermaid
erDiagram
    users ||--o| profiles : "1:1"
    users ||--o{ targets : "1:N"
    users ||--o| billing_accounts : "1:1"
    users ||--o{ food_entries : "1:N"
    users ||--o{ meal_nutrition_summaries : "1:N"
    users ||--o{ meal_recommendations : "1:N"
    users ||--o{ daily_nutrition_summaries : "1:N"
    users ||--o{ daily_nutrition_reports : "1:N"
    users ||--o{ daily_target_snapshots : "1:N"

    targets ||--o{ target_nutrients : "1:N"
    targets ||--o{ daily_target_snapshots : "N:1 (SET NULL)"

    daily_target_snapshots ||--o{ daily_target_snapshot_nutrients : "1:N"

    meal_nutrition_summaries ||--o{ meal_nutrition_nutrients : "1:N"

    daily_nutrition_summaries ||--o{ daily_nutrition_nutrients : "1:N"

    users {
        uuid id PK
        string email UK "unique, indexed"
        string hashed_password
        string name
        string plan "trial/free/paid"
        datetime trial_ends_at
        boolean has_profile
        datetime created_at
        datetime deleted_at
    }

    profiles {
        uuid user_id PK,FK "→ users.id (CASCADE)"
        string sex
        date birthdate
        float height_cm
        float weight_kg
        string image_id
        smallint meals_per_day
        datetime created_at
        datetime updated_at
    }

    targets {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        string title
        string goal_type
        text goal_description
        string activity_level
        boolean is_active "indexed, default=false"
        text llm_rationale
        text disclaimer
        datetime created_at
        datetime updated_at
    }

    target_nutrients {
        uuid target_id PK,FK "→ targets.id (CASCADE)"
        string code PK
        float amount_value
        string amount_unit
        string source
    }

    daily_target_snapshots {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date date "indexed"
        uuid target_id FK "→ targets.id (SET NULL)"
        datetime created_at
        unique "user_id, date"
    }

    daily_target_snapshot_nutrients {
        uuid snapshot_id PK,FK "→ daily_target_snapshots.id (CASCADE)"
        string code PK
        float amount_value
        string amount_unit
        string source
    }

    billing_accounts {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), unique"
        string stripe_customer_id "indexed"
        string stripe_subscription_id "indexed"
        string subscription_status "default='NONE'"
        string current_plan "default='free'"
        datetime updated_at
    }

    food_entries {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date date "indexed"
        string meal_type "main/snack, indexed"
        smallint meal_index
        string name
        float amount_value
        string amount_unit
        float serving_count
        text note
        datetime created_at
        datetime updated_at
        datetime deleted_at "indexed"
    }

    meal_nutrition_summaries {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date date "indexed"
        string meal_type "indexed"
        smallint meal_index
        datetime generated_at
        datetime updated_at
        unique "user_id, date, meal_type, meal_index (when not null)"
        unique "user_id, date, meal_type (when meal_index is null)"
    }

    meal_nutrition_nutrients {
        uuid summary_id PK,FK "→ meal_nutrition_summaries.id (CASCADE)"
        string code PK
        float amount_value
        string amount_unit
        string source
    }

    meal_recommendations {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date generated_for_date "indexed"
        text body
        text[] tips "default=[]"
        datetime created_at
        unique "user_id, generated_for_date"
    }

    daily_nutrition_summaries {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date date "indexed"
        datetime generated_at
        datetime updated_at
        unique "user_id, date"
    }

    daily_nutrition_nutrients {
        uuid summary_id PK,FK "→ daily_nutrition_summaries.id (CASCADE)"
        string code PK
        float amount_value
        string amount_unit
        string source
    }

    daily_nutrition_reports {
        uuid id PK
        uuid user_id FK "→ users.id (CASCADE), indexed"
        date date "indexed"
        text summary
        text[] good_points "default=[]"
        text[] improvement_points "default=[]"
        text[] tomorrow_focus "default=[]"
        datetime created_at
        unique "user_id, date"
    }
```

## テーブル一覧と説明

### ユーザー関連

1. **users** - ユーザー基本情報

   - プラン情報（trial/free/paid）、プロフィール有無フラグを含む

2. **profiles** - ユーザープロフィール

   - users と 1:1 の関係（user_id が PK かつ FK）
   - 性別、生年月日、身長、体重、1 日の食事回数などを保持

3. **billing_accounts** - 請求アカウント
   - users と 1:1 の関係
   - Stripe の顧客 ID、サブスクリプション ID を保持

### 目標設定関連

4. **targets** - 目標設定

   - users と 1:N の関係
   - 目標タイプ、活動レベル、アクティブフラグなどを保持

5. **target_nutrients** - 目標栄養素

   - targets と 1:N の関係
   - 複合主キー（target_id, code）

6. **daily_target_snapshots** - 日次目標スナップショット

   - users と 1:N の関係
   - targets と N:1 の関係（SET NULL で削除可能）
   - 1 ユーザー 1 日 1 レコード（user_id, date でユニーク）

7. **daily_target_snapshot_nutrients** - 日次目標スナップショット栄養素
   - daily_target_snapshots と 1:N の関係
   - 複合主キー（snapshot_id, code）

### 食事ログ関連

8. **food_entries** - 食事ログ

   - users と 1:N の関係
   - 1 品分の食事情報を保持（main/snack の区別あり）
   - ソフトデリート対応（deleted_at）

9. **meal_nutrition_summaries** - 食事栄養サマリ

   - users と 1:N の関係
   - 1 日の各食事（main/snack）の栄養サマリを保持
   - 複雑なユニーク制約（meal_index が NULL の場合と非 NULL の場合で異なる）

10. **meal_nutrition_nutrients** - 食事栄養素

    - meal_nutrition_summaries と 1:N の関係
    - 複合主キー（summary_id, code）

11. **meal_recommendations** - 食事推奨
    - users と 1:N の関係
    - 1 ユーザー 1 日 1 レコード（user_id, generated_for_date でユニーク）

### 日次栄養関連

12. **daily_nutrition_summaries** - 日次栄養サマリ

    - users と 1:N の関係
    - 1 ユーザー 1 日 1 レコード（user_id, date でユニーク）

13. **daily_nutrition_nutrients** - 日次栄養素

    - daily_nutrition_summaries と 1:N の関係
    - 複合主キー（summary_id, code）

14. **daily_nutrition_reports** - 日次栄養レポート
    - users と 1:N の関係
    - 1 ユーザー 1 日 1 レコード（user_id, date でユニーク）
    - サマリ、良い点、改善点、明日のフォーカスを保持

## 主なリレーションシップ

- **users → profiles**: 1:1（CASCADE 削除）
- **users → billing_accounts**: 1:1（CASCADE 削除）
- **users → targets**: 1:N（CASCADE 削除）
- **users → food_entries**: 1:N（CASCADE 削除）
- **users → meal_nutrition_summaries**: 1:N（CASCADE 削除）
- **users → meal_recommendations**: 1:N（CASCADE 削除）
- **users → daily_nutrition_summaries**: 1:N（CASCADE 削除）
- **users → daily_nutrition_reports**: 1:N（CASCADE 削除）
- **users → daily_target_snapshots**: 1:N（CASCADE 削除）
- **targets → target_nutrients**: 1:N（CASCADE 削除）
- **targets → daily_target_snapshots**: N:1（SET NULL 削除）
- **daily_target_snapshots → daily_target_snapshot_nutrients**: 1:N（CASCADE 削除）
- **meal_nutrition_summaries → meal_nutrition_nutrients**: 1:N（CASCADE 削除）
- **daily_nutrition_summaries → daily_nutrition_nutrients**: 1:N（CASCADE 削除）
