# マルチエージェント実行基盤 インフラ構成比較 検証ログ

> ステータス: 進行中
> 作成日: 2026/06/03
> 最終更新: 2026/06/03（壁打ち整理を反映）
> ファイルパス: /Users/shogo/Documents/ai-business-os/15_ナレッジ基盤/vault/structured/projects/20260603_multi-agent-infra-comparison.md

---

📋 プロジェクト概要
* カテゴリ: AIエージェント実行基盤 / インフラ構成比較（VPS・物理PC・AWS・GCP・PaaS）
* 期間: 2026/06/03 -（検証中・Phase 0 構成整理のみ）
* 主要メンバー: shogo
* ステークホルダー: shogo（AI 事業 OS オーナー）、将来的にクライアント（API 提供先）
* プロジェクトステータス: 進行中

> このログは「今すぐ本番構築する」ためではなく、後から再検討するときに壁打ち結果を引き出せるようにするための整理メモ。Phase 0（構成パターンの洗い出しと比較）までを記録する。

---

## 1. 背景と目的

* **目的**: Claude Code / Hermes Agent / browser-use / Playwright などを使い、複数の AI エージェントを実行できる環境を作る場合、どのインフラ構成が考えられるかを整理しておく
* **検討対象の置き場所**: VPS / 物理PC・ミニPC / AWS / Google Cloud / Fly.io・Railway・Koyeb・Render などの PaaS・サーバーレスコンテナ / 将来の役割別コンテナ分離
* **中心テーマ**: 単なる Web アプリのホスティングではなく「エージェント実行基盤」をどう作るか
* **想定する処理フロー**:
  * 外部ツール / n8n / Make / Webhook → HTTP エンドポイント → FastAPI / Express → Claude Code / Hermes / browser-use → Playwright / Chromium / CLI / Shell → LLM API / ローカルLLM → JSON で結果を返す
* **前提（重要）**: 今回作りたいものは普通の軽量 API サーバーではなく「リモートに置く AI 実行端末」に近い。API の中で CLI 実行・自律ブラウザ操作・Chromium 起動・長めの LLM 推論・複数ステップのエージェントループ・ファイル生成・作業ログ保存などが走る
* **前提を間違えると起きる問題**: Cloud Run / Lambda / 無料 PaaS に寄せすぎると、メモリ不足・Chromium が起動しない・タイムアウト・コールドスタートが重い・作業状態を残しにくい・複数エージェントの干渉・デバッグ困難・RDP/SSH で中身を見られない、といった不整合が出やすい
* **思想のズレ**: Claude Code / Hermes Agent は「OS・シェル・ファイルシステム・作業ディレクトリがあり CLI を起動できる」世界観が前提。これは VPS・VM・物理PC・コンテナホストと相性が良く、ステートレス短時間処理が得意なサーバーレスとはやや噛み合わない

---

## 2. 取り組み内容

### 実施した施策・活動

* 2026/06/03: エージェント実行基盤の構成パターンを洗い出し、VPS / 物理PC / AWS（EC2・Lightsail・ECS Fargate・ECS Express Mode・App Runner・Lambda）/ GCP（Cloud Run・Compute Engine・GKE）/ PaaS（Fly.io・Railway・Koyeb・Render）を横断比較
* 各パターンの構成イメージ・メリット・デメリット・向き不向き・星評価を整理
* 推奨スペック（Claude Code 単体 / Hermes / browser-use 込み / 役割別複数）の目安を整理
* 役割別エージェント組織（research / sales / recruiting / browser / orchestrator）の設計案、セキュリティ設計、ロードマップ、再検討時チェックリストを整理

### 使用したツール・技術

* エージェント: Claude Code / Hermes Agent / browser-use
* ブラウザ: Playwright / Chromium
* Web サーバー: FastAPI / Express
* コンテナ: Docker Engine / Docker Compose
* リバースプロキシ / 公開: Caddy / Nginx / ALB / Cloudflare Tunnel / Tailscale
* オーケストレーション入口: n8n / Make / Webhook
* 非同期化候補: Redis / SQLite / Postgres / SQS / Celery / RQ / BullMQ

### 主要な意思決定とその理由

* **サーバーレスではなく「常時使える実行マシン」を基本に置く**: browser-use / Playwright を含む複数エージェント運用では、メモリ・ブラウザ・ログ・デバッグ・状態保持の観点で、普通の Linux マシン上に Docker Compose で立てるのが最もわかりやすい
* **基本アーキテクチャは同期型から始め、重くなったら非同期型へ**:
  * 同期型（`POST /research/run` → browser-use 実行 → 結果 JSON 返却）: 構成がシンプルで n8n の HTTP Request ノードと相性が良く PoC 向き。ただし処理が長いとタイムアウトしやすい
  * 非同期型（`POST /jobs` → job_id 即返し → 裏で実行 → 完了後に Webhook へ POST）: 長時間処理に強く実務運用向きだが、job_id 管理・キュー・再実行設計が必要
* **第一候補は VPS + Docker Compose**、自分用検証は UbuntuミニPC + Docker Compose

---

## 3. 進捗と成果

### 達成できたこと

* 主要な置き場所パターンを一覧化し、星評価付きで比較表に整理（下記）
* 用途別の推奨スペック目安を確定
* 段階的に育てるロードマップ（Phase 0〜5）を定義

### 定量的な成果 — パターン別比較サマリー

| パターン | 初期費用 | 月額 | 自由度 | 安定性 | 外部公開 | 複数エージェント | デバッグ | 本番向き | 総合コメント |
|---|---|---|---|---|---|---|---|---|---|
| VPS | 低 | 低〜中 | 高 | 中〜高 | 簡単 | 高 | 高 | 中〜高 | 最もバランス良・第一候補 |
| 物理PC / ミニPC | 中 | 低（電気代） | 最高 | 回線次第 | 工夫必要 | 高 | 最高 | 自社用途向き | 自分用の実験基盤として有力 |
| AWS EC2 | 低 | 中 | 高 | 高 | 簡単 | 高 | 高 | 高 | AWS前提なら現実的 |
| AWS Lightsail | 低 | 中 | 高 | 中〜高 | 簡単 | 中 | 中〜高 | 中 | AWS内で簡単に始める用 |
| AWS ECS Fargate | 低 | 中〜高 | 中 | 高 | やや複雑 | 非常に高 | 中 | 高 | 本番の役割別分離の本命 |
| AWS ECS Express Mode | 低 | 中〜高 | 中 | 高 | 簡単寄り | 高 | 中 | 高 | App Runner 代替候補 |
| AWS App Runner | — | — | — | — | — | — | — | 非推奨 | 新規採用は基本見送り |
| AWS Lambda コンテナ | 低 | 安い | 低 | 中〜高 | 簡単 | 低 | 低 | 中 | 自律ループには窮屈・見送り寄り |
| GCP Cloud Run | 低 | 低〜中 | 中 | 高 | 簡単 | 中 | 中 | 良い（今回制約あり） | 技術的に良いが請求アカウントがネック |
| GCP Compute Engine | 低 | 中 | 高 | 高 | 簡単 | 高 | 高 | 高 | GCP版EC2・今回は優先度低 |
| GCP GKE | 低 | 高 | 最高 | 高 | やや複雑 | 最高 | 中 | 高 | 今回は過剰・見送り |
| Fly.io | 低 | 低〜中 | 中〜高 | 中〜高 | 簡単 | 中〜高 | 中 | 中 | Cloud Run 代替として有力 |
| Railway | 低 | 中 | 中 | 中 | 簡単 | 中 | 中 | PoC向き | とにかく早く試す用 |
| Koyeb | 低 | 中 | 中 | 中〜高 | 簡単 | 中 | 中 | 中 | Cloud Run 代替候補 |
| Render | 低 | 中 | 中 | 中 | 簡単 | 中 | 中 | 普通のWeb向き | browser-use にはやや弱い |

### 定量的な成果 — 推奨スペック目安

| 用途 | 最低 | 推奨 | 余裕 / 複数同時 |
|---|---|---|---|
| Claude Code 単体（推論はクラウド側） | 2 vCPU / 4GB | 2〜4 vCPU / 8GB | — |
| Hermes Agent（メモリ・ツール・ブラウザ込み） | 2 vCPU / 4GB | 4 vCPU / 8GB | 4〜8 vCPU / 16GB |
| browser-use / Playwright / Chromium 込み（最も重い） | 2 vCPU / 4GB | 4 vCPU / 8GB | 4〜8 vCPU / 16GB 以上 |
| 役割別エージェント複数 | — | 8GB | 16GB あると安心 |

* browser-use は Chromium を使うため CLI エージェントよりメモリを食う。動的/SPA/ログイン付きサイトでは 4GB はカツカツになりうる
* 役割別複数の場合、各エージェントが常時ブラウザを起動するのは避け、ブラウザ操作だけ専用コンテナに切り出すかジョブ実行時のみ Chromium を起動する

### 定性的な成果

* 「クラウドに何を置くか」ではなく「AI エージェント用の実行端末をどう設計するか」という問題設定に再定義できた
* 満たすべき条件＝Docker で持ち運べる／HTTP で外部から呼べる／役割ごとに分離できる／ログと状態を追える／ブラウザ操作に耐えるスペック／必要時に RDP・SSH で中身を見られる

---

## 4. 学びとナレッジ

### うまくいったこと（Good）— パターン別の強み

* **VPS**: 月額固定でコストが読みやすい（月1,000〜5,000円）／Docker Compose で役割別エージェントを増やしやすい／SSH で `docker logs`・`docker exec` でき browser-use のトラブルに強い／CLI エージェントと相性良／クライアントには API URL + Bearer だけ渡せる
* **物理PC / ミニPC**: 自由度が最高（Ollama / LM Studio / ローカルLLM も同居可）／長時間処理に強い／RDP で GUI 確認しやすい／月額はほぼ電気代／GPU 付きならローカルモデルも
* **AWS ECS Fargate**: 役割ごとのコンテナを強く分離／タスク単位で CPU・メモリ・IAM を分離／Secrets Manager と相性良／実行後に破棄する設計が可能／本番向き
* **GCP Cloud Run**: Docker をそのままデプロイ・HTTPS が簡単・スケール to ゼロ・PoC に非常に向く（技術面）
* **Fly.io / Railway / Koyeb**: Dockerfile をそのまま使え、PoC を素早く外部公開できる

### うまくいかなかったこと / 注意点（Bad）

* **VPS**: OS/Docker/SSH鍵/FW/HTTPS/バックアップ等の管理が必要／1台構成は単一障害点／Docker はカーネル共有で VM ほど強く分離できない／自動スケールは基本なし
* **物理PC**: 初期費用（中古ミニPC 2〜5万、新品 3〜10万、GPU付 10万〜）／自宅・事務所の直接公開は避けるべき／停電・回線障害・故障に弱い／クライアント本番提供にはやや不向き
* **AWS Fargate**: 構成が複雑・ALB/VPC 設計が必要・ログ確認が EC2 より面倒・小規模 PoC には重い
* **GCP（Cloud Run / Compute Engine）**: 請求先アカウント・クレジットカード紐づけが必須。今回のクライアント環境ではこれがネックで使えない可能性が高く、本命から外す
* **PaaS（Fly.io / Railway / Koyeb / Render）**: 従量課金のため browser-use のような重い処理を繰り返すとコストが読みにくい。Render は browser-use / Chromium にはやや窮屈

### 技術的な発見・Tips

* **ブラウザ操作の分離（2案）**:
  * 案1: 各エージェントが必要時に Chromium を起動 — シンプルで完全分離しやすいが、メモリ消費が増え同時実行で重い
  * 案2: `browser-agent` を共用サービス化 — 集中管理でき再起動も容易、メモリ制限を一箇所に集約できるが、設計が複雑でセッション/Cookie/profile 分離に注意。最初は案1、重くなったら案2
* **役割別で分離すべきもの**: APIキー / 環境変数 / Docker volume / ログ / 作業ディレクトリ / Cookie・browser profile / ネットワーク / 実行権限
* **混ぜない方がよいもの**: 営業データと採用データ / 顧客Aと顧客Bのデータ / 本番APIキーと検証APIキー / ログインCookie / 個人情報 / 社内機密
* **重要なのはホスティング代より LLM API 代**: 費用は「インフラ費 + LLM API費 + プロキシ/外部API費 + ストレージ費 + 運用保守コスト」で考える。トークン代が支配的になりやすい
* **OS は Ubuntu が素直**: Docker Engine / Playwright / SSH / systemd 常駐 / Caddy・Nginx の情報量の面で、Windows より Ubuntu 24.04 LTS が運用しやすい

---

## 5. 課題と対応

### 発生した課題（想定リスク）

* browser-use / Chromium のメモリ消費が大きく、4GB ではカツカツになりうる → 推奨 8GB、複数同時は 16GB 以上
* 同期型は重いサイトで数分かかりタイムアウトしやすい → 非同期ジョブ化（`POST /jobs` → job_id → Webhook 返却）で対応
* Docker コンテナはカーネル共有で VM ほど強く分離できない → 機密/個人情報を扱う本番は VPS を分けるか Fargate に逃がす
* 物理PC の直接インターネット公開は危険 → Cloudflare Tunnel / Tailscale / WireGuard / VPS リバースプロキシ経由にする
* GCP（Cloud Run / Compute Engine）の請求アカウント・クレカ紐づけ問題 → 今回は GCP を本命から外す

### 対応方法（セキュリティ最低ライン）

* SSH は鍵認証・パスワード/rootログイン無効、UFW or Security Group でポート制限
* API は Bearer Token + HTTPS 必須、`.env` を Git に入れない、役割ごとに APIキーを分ける
* Docker は可能なら非root 実行、ログに APIキーを出さない、危険コマンドを制限
* RDP / SSH は直接公開せず、VPN / Tailscale 経由の「管理用」に限定（通常のエージェント実行経路にはしない）

### 未解決の課題

* browser-use がコンテナ内で安定起動するか、1リクエストの実行時間、同時実行耐性の実機検証は未実施（Phase 1 で確認）
* クライアントごとの分離方式（VPS分離 / コンテナ分離 / Fargate移行）の最終判断は未確定

---

## 6. コストとリソース

### 金銭的コスト（目安）

* **VPS**: 月額 1,000〜5,000円程度（4GB は安い、8〜16GB で上がる）
* **物理PC**: 初期 2万〜10万円（中古ミニPC 2〜5万 / 新品 3〜10万 / GPU付 10万〜）＋月額は電気代のみ
* **AWS**: EC2 / Fargate は VPS より割高になりやすい（EBS・転送量・Elastic IP 等の細かい課金）。ただし企業利用では説明しやすい
* **GCP**: Cloud Run は未使用時は安いが請求アカウントがネック
* **PaaS**: PoC には良いが従量課金で重い処理のコストが読みにくい

### コスト対効果

* インフラ費よりも LLM API のトークン代が支配的になりやすい点を前提にすべき
* 長く使うなら物理PC が最安だが、可用性・説明責任の面で本番には VPS が無難

---

## 7. 今後の展開

### 次のアクション（ロードマップ）

* **Phase 0（現在）**: 構成パターンの整理のみ（本ログ）。すぐには作らない
* **Phase 1**: 手元 or 物理PC（Ubuntu + Docker Compose）で `research-agent` 1体 + browser-use + Claude API + HTTP エンドポイントを検証。browser-use が安定起動するか／n8n から叩けるか／同期処理の所要時間／必要メモリ（4/8/16GB）を確認
* **Phase 2**: 手元で動いた Docker 構成をそのまま VPS（+ Caddy）へ移し、外部から安定して呼べるようにする
* **Phase 3**: 役割別エージェント（research / sales / recruiting）を増やし、env / volume / logs / APIトークン / route を分離
* **Phase 4**: 処理が長くなったら非同期ジョブ化（Redis / SQLite / Postgres / SQS / Celery / RQ / BullMQ 等）
* **Phase 5**: クライアント本番用に分離（VPS分離 / コンテナ分離 / APIキー分離 / Fargate 移行 / 顧客ごと専用環境）

### 横展開の可能性

* 将来的な「エージェント組織」像: research-agent / sales-agent / recruiting-agent / document-agent / browser-agent / orchestrator を Docker Compose で構成し、コンテナを足すだけで仮想組織図のように拡張
* 省伍さん側で VPS をホストし、クライアントには API URL + Bearer のみ提供する形でサービス化

### 長期的な改善案

* AWS 前提が通る案件では EC2 / Lightsail で開始し、本番分離フェーズで ECS Fargate / ECS Express Mode へ
* ローカルLLM（Ollama / LM Studio / vLLM）併用時は GPU 付き物理PC を実験基盤に

---

📚 関連リソース

### 成果物・ドキュメント

* 本ログ（構成パターン整理 / 比較表 / スペック目安 / ロードマップ）

### 参考資料

* （情報なし — 壁打ちベースのため外部URLなし）

### 関連プロジェクト

* [[20260528_browser-use-ecosystem]] — browser-use エコシステムのローカル検証とホスト候補の事前スクリーニング。本ログはその「hosting-plan 詳細比較版」に相当
* [[20260601_computer-use-browser-use-local-llm-survey]] — Computer Use / Browser Use / ローカルLLM の機能選択・用途別優先度（実行環境はスコープ外）
* [[20260110_async-agent-platform-design]] — チャットプラットフォーム向け非同期エージェント基盤の設計
* `16_検証ラボ/lab-browser-use-ecosystem/` — 各リポの report.md（VPS 常駐型の考察含む）

---

✅ メモ・雑記

* **結論**: Claude Code / Hermes Agent / browser-use を複数体動かす環境は、サーバーレスよりも VPS・VM・物理PC のような「常時使える実行マシン」と相性が良い。特に browser-use / Playwright を使うなら、普通の Linux マシン上に Docker Compose で立てるのが最もわかりやすい
* **最初の現実解**:
  * 自分用検証: UbuntuミニPC + Docker Compose
  * 外部API化: VPS + Docker Compose + Caddy
  * AWS前提: EC2 / Lightsail + Docker Compose → 将来 ECS Fargate / ECS Express Mode
  * GCP前提: Cloud Run が理想だが請求アカウント問題があれば今回は見送り
  * PaaS前提: Fly.io / Railway / Koyeb は PoC 候補
* 最初から完璧なクラウド設計にせず、まず `research-agent` 1体を n8n から HTTP で呼べるところまで確認 → 役割別コンテナ → 非同期ジョブ → VPS移行 → クライアント別分離の順で育てるのが、コスト・技術検証・安全性・拡張性のバランスが最良
* **再検討時チェックリスト（要点）**: 最初の用途（Web調査/営業リスト/採用調査/資料要約/ブラウザ操作）/ 実行方式（同期 or 非同期）/ 置き場所 / 必要スペック（4・8・16GB）/ エージェント数 / ブラウザ起動方式（各内 or 専用分離）/ データ保存（なし/volume/SQLite/Postgres/S3互換）/ セキュリティ（Bearer/IP制限/VPN/Tailscale/Tunnel）/ クライアントデータ（扱う・顧客ごと分離）

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/06/03 | ファイル作成（init）。壁打ちメモ（実行基盤インフラ構成比較）を PJ単位フォーマットに構造化 |
