# Git / GitHub 開発フロー（ライト版 GitHub Flow）

個人開発だけど、将来のチーム開発やポートフォリオも意識した
**「軽めだけどキレイな GitHub Flow」** の運用ルールをまとめる。

---

## 0. 目的・前提

- `main` ブランチは **常に動く / デプロイ可能** な状態を保つ。
- 新しい開発は基本的に **短命な作業ブランチを切って行う**。
- **1 ブランチ = 1 PR = 1 機能（または小さな修正）** を基本とする。
- レビューは自分一人だが、**PR を自分用のログ・メモとして残す**。

---

## 1. ブランチ戦略

### 1.1 ベースブランチ

- `main`

  - 唯一のベースブランチ。
  - 常にビルド可能・テストが通る状態を目指す。
  - リリース／デプロイは基本的に `main` 基準で行う。

### 1.2 ブランチ命名規則

用途ごとに以下のプレフィックスを付ける：

- 機能追加

  - `feature/<短い説明>`
  - 例：`feature/add-login`, `feature/meal-pagination`

- バグ修正

  - `fix/<短い説明>`
  - 例：`fix/login-error-message`

- 細かい調整・リファクタ・設定変更

  - `chore/<短い説明>`
  - 例：`chore/update-deps`, `chore/tweak-logging`

- 試験的な実装・実験（捨ててもよいコード）

  - `spike/<短い説明>`
  - 例：`spike/try-new-ui-lib`

> 原則として、`main` からだけブランチを生やす。
> 別の作業ブランチから作るのは極力避ける。

---

## 2. コミット戦略

### 2.1 粒度

- **意味のある小さなステップごとにコミット** する。
- できるだけコミットごとにテストが通る状態を意識する（完璧でなくても OK）。

例：

- `feat: add login form markup`
- `feat: wire login form to API`
- `fix: handle invalid credentials error`
- `chore: tidy styles around login form`

### 2.2 メッセージ方針

- 先頭に、ざっくりタイプを付ける（任意ルールだが揃えると見やすい）：

  - `feat:` 機能追加
  - `fix:` バグ修正
  - `chore:` 雑多な変更（設定、依存ライブラリなど）
  - `refactor:` 挙動を変えない内部改善
  - `docs:` ドキュメント変更

---

## 3. 日々の開発フロー

### 3.1 作業開始時

1. ベースの `main` を最新化する：

   ```bash
   git switch main
   git pull origin main
   ```

2. 新しい作業ブランチを切る：

   ```bash
   git switch -c feature/<短い説明>
   # 例:
   # git switch -c feature/add-login
   ```

### 3.2 実装中

1. コードを編集する。

2. ある程度まとまったらコミット：

   ```bash
   git status          # 変更確認
   git add .
   git commit -m "feat: add login API"
   ```

3. こまめに push しておく：

   ```bash
   git push -u origin feature/add-login
   ```

> ※ CI（GitHub Actions）を使う場合、
> `push` をトリガーに lint / テストを走らせる。

### 3.3 Pull Request の作成

1. GitHub 上で、そのブランチから `main` 向けに Pull Request を作成。
2. PR には以下を簡潔に書く：

   - 目的（何をしたか）
   - 変更点の概要
   - 確認した動作（簡単でよい）

例（PR 説明テンプレ）：

```text
## 概要
- ログインフォームを追加
- /api/login にリクエストを送る処理を実装

## 動作確認
- 正しいメール・パスワードでログインできること
- 不正な場合にエラーメッセージが表示されること
```

### 3.4 CI & 自己レビュー

- PR 作成時に `on: pull_request` をトリガーに CI を実行。

  - 例：Lint、ユニットテスト、型チェックなど。

- 差分を自分で確認し、

  - 不要なデバッグコードの削除
  - 名前の微修正
  - 変なロジックがないか
    をチェックする。

### 3.5 マージとブランチ削除

1. CI がすべて成功していることを確認。
2. 自分で `Merge pull request` ボタンを押して `main` にマージ。
3. マージ後、GitHub の `Delete branch` ボタンで **リモートブランチを削除**。
4. ローカルでも削除：

   ```bash
   git switch main
   git pull origin main
   git branch -d feature/add-login
   ```

> **原則：「1 ブランチ＝ 1 PR ＝ 1 機能」。
> マージされたブランチは役目終了として削除する。**

---

## 4. 連続した開発の進め方

### 4.1 同じ機能の「続き」を実装したい場合

- すでに PR をマージしている場合でも、**同じブランチを使い回さない**。
- もう一度 `main` から新しいブランチを切る。

```bash
git switch main
git pull origin main
git switch -c feature/add-login-validation
```

> 「続き」は新しいブランチと新しい PR として扱うことで、
> 履歴が読みやすく、トラブル時の切り戻しも簡単になる。

---

## 5. ブランチの掃除

### 5.1 マージ済みブランチの整理（ローカル）

マージ済みブランチの一覧を確認：

```bash
git branch --merged
```

不要なものを、安全に削除：

```bash
git branch -d feature/add-login
git branch -d fix/header-style
```

### 5.2 マージ済みブランチの整理（リモート）

PR がマージされたタイミングで GitHub の UI から `Delete branch` を押す。
または CLI で：

```bash
git push origin --delete feature/add-login
```

---

## 6. 例外扱い：実験や危険な変更

- 大きなリファクタ・実験的な変更は `spike/` ブランチを利用する。
- `spike/` ブランチは、マージせずに削除しても構わない前提で使う。

例：

```bash
git switch main
git pull origin main
git switch -c spike/try-new-orm
```

---

## 7. 参考コマンド一覧

```bash
# main を最新化
git switch main
git pull origin main

# 新しいブランチを作成して切り替え
git switch -c feature/add-login

# 変更の確認
git status

# 変更をステージング
git add .

# コミット作成
git commit -m "feat: add login API"

# リモートへ初回 push（追跡ブランチ設定込み）
git push -u origin feature/add-login

# マージ済みブランチの一覧を確認
git branch --merged

# ローカルブランチ削除（安全版）
git branch -d feature/add-login

# リモートブランチ削除
git push origin --delete feature/add-login
```
