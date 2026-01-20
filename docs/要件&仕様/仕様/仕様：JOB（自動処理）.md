いいですね、ここまでで「毎日のパイプライン」の主要なピースが揃ってきたので、
それらを裏で回す JOB（自動処理） の仕様を整理していきます 💪

これまでと同じく：

概要
JOB ごとの要件・振る舞い
外部仕様（いつ・誰が・どう動くか）
内部仕様（UseCase / ポート / 設計）
の順でまとめます。

JOB（自動処理）の仕様 0. 概要
目的

アプリのコアとなる「毎日のサイクル」を、ユーザー操作だけに依存せず、
日付の切り替わり / 一日のタイミング に合わせて自動で整えていく。

現時点で想定している JOB は大きく 2 つ：

ターゲットスナップショット JOB
→ 日付を跨いだタイミングで「昨日のターゲット」を固定化する。

提案生成 JOB（Recommendation JOB）
→ 毎日一定時刻に「直近 5 日分レポートが揃っているユーザー」に対して自動で提案を生成する。

（将来的には、バッジ付与・古いデータのクリーンアップなども JOB 候補）

1. JOB 一覧と要件
   1-1. ターゲットスナップショット JOB
   名前（仮）： SnapshotActiveTargetForYesterdayJob

目的

「過去日のターゲット値を固定化」するために、
毎日 1 回、日付を跨ぐタイミングで 昨日の日付 の DailyTargetSnapshot を作成する。
要件

実行タイミング：

毎日 深夜〜早朝（例：00:05〜01:00 頃）の 1 回
対象：

アクティブユーザー全員（退会済みを除く）
やること（論理）：

システム時間から「今日（today）」を取得

yesterday = today - 1 日

全アクティブユーザーを取得

各ユーザーについて：

EnsureDailyTargetSnapshotUseCase.execute(user_id, yesterday) を呼ぶ

既に Snapshot があればそのまま
なければ、その時点の Active Target から DailyTargetSnapshot を生成・保存
Active Target が存在しないユーザーはスキップ（ログだけ出す）

結果

(user_id, date=yesterday) に対して必ず 0 or 1 の Snapshot が存在し、
一度作成された Snapshot は過去日のターゲットとして固定される。
1-2. 提案生成 JOB（Recommendation JOB）
名前（仮）： GenerateDailyMealRecommendationsJob

目的

毎日定時に、直近 5 日分の DailyNutritionReport が揃っているユーザーに対して、
「今日の提案」(MealRecommendation) を自動で生成する。
要件

実行タイミング：

毎日 朝〜昼前（例：07:00）に 1 回
対象：

アクティブユーザーのうち、UserPlan が TRIAL または PAID のユーザー
前提：

直近 5 日分の日次レポート DailyNutritionReport が存在するユーザーのみ。
やること（論理）：

システム時間から「今日（today）」を取得 → base_date = today

全アクティブユーザー一覧を取得

各ユーザーについて：

プランチェック：plan in {TRIAL, PAID} でない場合 → スキップ

GenerateMealRecommendationUseCase.execute(user_id, base_date) を呼ぶ

直近 5 日のレポート数が不足 → NotEnoughDailyReportsError → スキップ（ログのみ）
generated_for_date=base_date の Recommendation が既に存在 → MealRecommendationAlreadyExistsError → スキップ
それ以外のエラー → ログ出力（他ユーザー処理は続行）
正常に生成できた場合、そのユーザーには「今日の提案」が 1 件保存される。

結果

毎日、レポートが溜まっているユーザーには自動的に「今日の提案」が作られ、
ユーザーはアプリを開くだけで提案が見られる。 2. 外部仕様（どこからどう動くか）
2-1. スケジューリング（誰が呼ぶか）
JOB 自体は、アプリ内部のコードとして app/jobs/ 配下に実装される。

実際の起動は以下いずれか：

OS cron（コンテナ内 or ホスト）
CI/CD（GitHub Actions のスケジュール）
クラウド側のスケジューラ（AWS EventBridge / CloudWatch Events など）
例：

# 毎日 00:10 にターゲットスナップショット JOB

python -m app.jobs.snapshot_active_target_for_yesterday

# 毎日 07:00 に提案生成 JOB

python -m app.jobs.generate_meal_recommendations
2-2. ユーザーから見た挙動
ユーザーは直接 JOB を意識しない。
ただし以下のような UX として「結果」を感じる：
ターゲットスナップショット JOB

昨日以前の日付については、ターゲット値が「その当時のもの」で一貫している。
ターゲット定義を変えても、過去のレポートや評価が変な風に変わらない。
提案生成 JOB

朝アプリを開くと「今日の提案」がすでに存在する。
自分で提案ボタンを押さなくても、習慣化しやすい。 3. 内部仕様（UseCase / Repo / jobs/ 構成）
3-1. UseCase レイヤ（アプリケーション）
EnsureDailyTargetSnapshotUseCase（既に整理済）
責務：

(user_id, date) について DailyTargetSnapshot を「必ず用意する」。

既にあればそれを返す。
なければ Active Target をもとに新規作成 → 保存 → 返す。
JOB からの使い方：

ターゲットスナップショット JOB は、ユーザーごとにこれを呼ぶことで実装される。
GenerateMealRecommendationUseCase（既に整理済）
責務：

(user_id, base_date) について、必要条件を満たす場合に MealRecommendation を生成。
JOB からの使い方：

提案生成 JOB は、ユーザーごとに execute(user_id, base_date=today) を呼ぶ形で実行する。
3-2. JOB 実装（app/jobs/）
3-2-1. ターゲットスナップショット JOB
パス例： app/jobs/snapshot_active_target_for_yesterday.py

論理コードイメージ：

def run_snapshot_active_target_for_yesterday_job() -> None:
today = clock.now().date()
yesterday = today - timedelta(days=1)

    users = user_repo.list_active_users()

    for user in users:
        try:
            ensure_daily_snapshot_uc.execute(user_id=user.id, date_=yesterday)
            log_ok(...)
        except ActiveTargetNotFoundError:
            log_skip_no_active_target(...)
        except Exception as e:
            log_error(...)

user_repo.list_active_users()：退会していないユーザー全員。
ensure_daily_snapshot_uc：EnsureDailyTargetSnapshotUseCase の DI。
3-2-2. 提案生成 JOB
パス例： app/jobs/generate_meal_recommendations.py

論理コードイメージ：

def run_generate_meal_recommendations_job() -> None:
today = clock.now().date()
users = user_repo.list_active_users()

    for user in users:
        try:
            # プランがFREEならスキップ（UC内でチェックしてもよい）
            if user.plan not in (UserPlan.TRIAL, UserPlan.PAID):
                log_skip_free_plan(...)
                continue

            recommendation = generate_reco_uc.execute(
                user_id=user.id,
                base_date=today,
            )
            log_ok(...)

        except NotEnoughDailyReportsError:
            log_skip_not_enough_reports(...)
        except MealRecommendationAlreadyExistsError:
            log_skip_already_exists(...)
        except Exception as e:
            log_error(...)

generate_reco_uc：GenerateMealRecommendationUseCase の DI。
エラーはロギングしつつ、他のユーザー処理は継続する。
3-3. DI / コンテナとの関係
app/di/container.py にそれぞれの UC を組み立てるファクトリを用意：

get_ensure_daily_target_snapshot_use_case()
get_generate_meal_recommendation_use_case()
JOB スクリプトは基本的に：

session = get*session()
user_repo = SqlAlchemyUserRepository(session)
各 UC = get*...( )
clock = get_clock()
を組み立てて実行する。 4. 将来的な拡張候補（メモ）
※今すぐ実装ではなく、「JOB レイヤに載せられると良いもの」の候補：

バッジ付与 JOB

毎日、各ユーザーの「記録完了状態」を集計して、
達成条件を満たしたバッジを自動付与する。
古いデータのクリーンアップ JOB

deleted_at が一定期間前の FoodEntry や Session レコードを削除する。
集計・分析用スナップショット JOB

週次 / 月次の栄養サマリを別テーブルに積んでおくなど。 5. まとめ（JOB 仕様のキモ）
ターゲットスナップショット JOB

過去日のターゲット値を「当時のアクティブターゲット」で固定化するための JOB。
毎日 1 回、昨日の日付に対して Snapshot を作る。
提案生成 JOB

直近 5 日レポートが揃っている TRIAL/PAID ユーザーに対して、
毎日自動で「今日の提案」を生成するための JOB。
設計上のポイント

どちらの JOB も「アプリケーション層の UC を呼び出すだけ」にすることで、
手動トリガー（API）とロジックを共有できるようにしておく。
失敗はログとして残しつつ、他ユーザーへの処理は継続する ベストエフォート型 の設計。
この仕様をベースに、app/jobs/ の各スクリプトと di/container.py の DI を整えていけば、
「人が何もしなくても毎日適切にスナップショットと提案が用意される」状態を作れるはずです 💡
