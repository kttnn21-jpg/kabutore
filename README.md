# kabutore

日本株のkabuステーションAPI向けに、放置運用寄りの自動売買ボット土台（紙運用のみ）を提供します。

## 重要な注意点
- **kabuステーションが起動しているWindows PC上での実行が前提**です。
- **初回は paper（売買なし）で動作確認**を行い、live 発注は後続で解放します。
- **秘密情報（.env）をコミットしない**でください。

## 機能概要
- 市場時間のみ稼働（平日 9:00-11:30 / 12:30-15:30 JST）
- STOP ファイル検知で即終了
- リスク上限の枠組み（注文回数上限・日次損失上限など）
- jsonl 形式のログ保存（`data/logs`）
- json 形式の state 保存（`data/state`）

## セットアップ（PowerShell）
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# .env を編集して必要な値を設定
python -m src.main
```

## 環境変数
`.env.example` を参考に設定してください。

- `KABU_API_BASE_URL`: kabuステーションAPIのベースURL
- `KABU_API_PASSWORD`: APIパスワード
- `MAX_ORDERS_PER_DAY`: 1日あたりの最大注文数（paperでもカウント）
- `MAX_DAILY_LOSS_PCT`: 1日あたりの最大損失率
- `MAX_POSITIONS`: 保有上限
- `MAX_YEN_PER_SYMBOL`: 銘柄あたりの上限金額
- `STOP_FILE`: 停止ファイル名（デフォルト `STOP`）
- `LOOP_INTERVAL_SEC`: 市場内のループ間隔
- `OUT_OF_MARKET_SLEEP_SEC`: 市場外の待機間隔
- `ERROR_MAX_COUNT`: 連続エラー上限
- `LOG_DIR`: ログ保存先
- `STATE_DIR`: state 保存先

## 運用方法
1. kabuステーションを起動し、API利用設定を有効化します。
2. `.env` に必要事項を記入します。
3. `python -m src.main` を実行します。
4. 停止したい場合は `STOP` ファイルを作成します。

## これから追加予定
- live 発注（sendorder）の実装
- 実運用向けの戦略とリスク管理強化
