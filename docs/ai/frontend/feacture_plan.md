チュートリアル＆バッジ機能 実装計画

  🔍 現在のコードベース構造分析

  フロントエンド (Feature-Sliced Design)
  /workspace/frontend/src/
  ├── modules/          # 8個の機能モジュール
  │   ├── auth/         # 認証
  │   ├── calendar/     # カレンダー表示
  │   ├── meal/         # 食事管理
  │   ├── nutrition/    # 栄養計算
  │   ├── profile/      # プロフィール
  │   ├── report/       # レポート
  │   ├── target/       # 目標設定
  │   └── today/        # 今日のサマリー

  バックエンド (Clean Architecture)
  /workspace/backend/app/
  ├── domain/          # 7個のドメイン
  │   ├── auth/        # 認証
  │   ├── billing/     # 課金
  │   ├── calendar/    # カレンダー
  │   ├── meal/        # 食事
  │   ├── nutrition/   # 栄養
  │   ├── profile/     # プロフィール
  │   └── target/      # 目標

  ---
  🎯 1. チュートリアル機能の設計・計画

  機能要件

  チュートリアルタイプ

  1. オンボーディングチュートリアル -
  初回ユーザー向けの基本操作ガイド
  2. フィーチャーチュートリアル -
  新機能紹介時のスポットライト
  3. インタラクティブガイド -
  実際の操作を促すステップバイステップ

  チュートリアル対象画面

  - /profile - プロフィール設定
  - /target - 栄養目標設定
  - /today - 食事記録・栄養分析
  - /calendar - カレンダー表示・レポート

  技術設計

  フロントエンド新規モジュール: tutorial/

  // modules/tutorial/
  ├── contract/
  │   └── tutorialContract.ts     #
  チュートリアル状態・ステップ型定義
  ├── model/
  │   └── useTutorialModel.ts     # 進行状態管理
  (TanStack Query)
  ├── ui/
  │   ├── TutorialOverlay.tsx     #
  オーバーレイ・スポットライト
  │   ├── TutorialTooltip.tsx     #
  ツールチップ・吹き出し
  │   └── TutorialProgress.tsx    # 進行状況表示
  └── api/
      └── tutorialClient.ts       #
  チュートリアル進行状況API

  バックエンド新規ドメイン: domain/tutorial/

  # domain/tutorial/
  ├── entities/
  │   ├── tutorial.py           # 
  チュートリアルエンティティ
  │   └── tutorial_progress.py  # 進行状況エンティティ
  ├── value_objects/
  │   └── tutorial_step.py      # 
  ステップ・状態値オブジェクト
  ├── repositories/
  │   └── tutorial_repository.py
  └── use_cases/
      ├── get_tutorial_progress.py
      └── update_tutorial_progress.py

  ---
  🏆 2. バッジ機能の設計・計画

  機能要件

  バッジカテゴリ

  1. 基本操作バッジ - 初回食事記録、プロフィール完成等
  2. 継続バッジ - 7日連続記録、30日連続記録等
  3. 栄養バランスバッジ -
  PFCバランス達成、ビタミン摂取等
  4. 特別バッジ - 特定イベント・シーズナルバッジ

  バッジ取得条件例

  const badgeConditions = [
    { id: 'first_meal', name: '初回食事記録',
  condition: '食事を1回記録' },
    { id: 'profile_complete', name:
  'プロフィール完成', condition:
  '基本情報をすべて入力' },
    { id: 'streak_7', name: '1週間継続', condition:
  '7日連続で記録' },
    { id: 'pfc_balance', name: 'PFCバランサー',
  condition: 'PFCバランス80%以上達成' },
    { id: 'nutrition_master', name: '栄養マスター',
  condition: '全栄養素90%以上達成' }
  ]

  技術設計

  フロントエンド新規モジュール: badge/

  // modules/badge/
  ├── contract/
  │   └── badgeContract.ts        #
  バッジ型定義・取得条件
  ├── model/
  │   └── useBadgeModel.ts        # バッジ状況管理
  ├── ui/
  │   ├── BadgeCollection.tsx     # バッジ一覧表示
  │   ├── BadgeNotification.tsx   # 取得時のお祝い表示
  │   └── BadgeProgress.tsx       # 取得進行状況
  └── api/
      └── badgeClient.ts          # バッジAPI

  バックエンド新規ドメイン: domain/badge/

  # domain/badge/
  ├── entities/
  │   ├── badge.py              # 
  バッジ定義エンティティ
  │   └── user_badge.py         # ユーザー取得バッジ
  ├── value_objects/
  │   ├── badge_condition.py    # 取得条件
  │   └── badge_category.py     # カテゴリ
  ├── services/
  │   └── badge_evaluator.py    # 取得条件判定ロジック
  └── use_cases/
      ├── evaluate_badges.py    # バッジ取得判定
      └── get_user_badges.py    # ユーザーバッジ取得

  ---
  🚀 3. 実装優先順位と依存関係

  フェーズ1: 基盤整備 (1-2週間)

● 推奨実装順序

  🏆 バッジ機能を優先実装する理由

  1. ユーザーエンゲージメント即効性 -
  ゲーミフィケーション要素で継続率向上
  2. 既存機能との親和性 -
  現在の食事記録・栄養分析データを活用可能
  3. 技術的シンプルさ - チュートリアルよりもUIが単純

  フェーズ1: バッジ基盤整備 ⭐ 最優先

  1. バックエンド: domain/badge/ ドメイン実装
  2. バックエンド: バッジ判定ロジック
  (badge_evaluator.py) 
  3. バックエンド: API エンドポイント (/api/v1/badges)
  4. フロントエンド: modules/badge/ 基本構造
  5. フロントエンド: BadgeNotification コンポーネント

  フェーズ2: 基本バッジ実装

  1. 基本操作バッジ (初回食事、プロフィール完成)
  2. 継続バッジ (7日連続記録)
  3. バッジ表示UI (today画面に統合)
  4. バッジ取得時の通知システム

  フェーズ3: チュートリアル実装

  1. バックエンド: domain/tutorial/ ドメイン実装
  2. フロントエンド: TutorialOverlay コンポーネント
  3. オンボーディング用チュートリアル (/profile,
  /target)
  4. 既存画面へのチュートリアルガイド統合

  フェーズ4: 高度な機能

  1. 栄養バランスバッジ (PFCバランス達成等)
  2. インタラクティブチュートリアル
  3. 特別バッジ・シーズナルバッジ
  4. バッジ共有機能

  ---
  💡 技術的考慮事項

  データベース設計

  -- badges テーブル
  CREATE TABLE badges (
      id VARCHAR PRIMARY KEY,
      name VARCHAR NOT NULL,
      description TEXT,
      icon VARCHAR,
      category VARCHAR,
      condition_type VARCHAR,
      condition_value JSONB,
      created_at TIMESTAMP
  );

  -- user_badges テーブル  
  CREATE TABLE user_badges (
      user_id UUID REFERENCES users(id),
      badge_id VARCHAR REFERENCES badges(id),
      earned_at TIMESTAMP,
      PRIMARY KEY (user_id, badge_id)
  );

  リアルタイム判定のタイミング

  - 食事記録後
  - 栄養分析完了後
  - プロフィール更新後
  - 日次バッチ処理

  ---

● 📝 実装計画 - 最終まとめ

  🎯 推奨アプローチ: バッジ機能優先

  理由:
  1. 即効性 - ユーザーエンゲージメント向上が速い
  2. 活用性 - 既存の栄養データを直接活用可能
  3. シンプルさ - UI/UX的に実装しやすい

  📅 実装スケジュール提案

  Week 1-2: バッジ基盤
  - バックエンド: domain/badge/ 実装
  - 基本バッジ5種類の定義・判定ロジック

  Week 3-4: バッジUI
  - フロントエンド: modules/badge/ 実装
  - 通知システム・バッジ表示UI

  Week 5-8: チュートリアル
  - バックエンド: domain/tutorial/ 実装
  - オンボーディングフロー完成

  ---
  次の一歩: どちらの機能から実装を始めますか？

  1. 🏆 バッジ機能 - エンゲージメント即効性重視
  2. 🎓 チュートリアル機能 -
  UX改善・新規ユーザー体験重視

  どちらを選択いただければ、具体的な実装作業に入ります
  ！