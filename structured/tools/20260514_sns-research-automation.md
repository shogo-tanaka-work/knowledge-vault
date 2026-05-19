---
title: SNSリサーチ業務のAI自動化 線引きマップ 2026年5月版
date: 2026-05-14
updated: 2026-05-15
tags: [sns, tiktok, youtube, instagram, automation, vlm, research]
status: draft
---

# SNSリサーチ業務のAI自動化 線引きマップ 2026年5月版

> 2026-05-15 更新: VLM世代を Gemini 2.5 系 → **Gemini 3 系/3.1 Pro**、TwelveLabs Pegasus 1.2 → **Pegasus 1.5（2026/4）**、Marengo 3.0は2025/11 GA に修正。SNS API側はX従量課金移行（2026/2）・Instagram スキップ率API正式化（2026/4）・TikTok Content Posting API の新機能（Duet/Stitch・写真投稿・ジオターゲ・Webhook）を追記。

## TL;DR

自社SNS運用代行のリサーチ工程を「どこまでAIで自動化できるか」を見極めるための市場調査ログ。3観点（①トレンド収集API、②動画中身のVLM解析、③自動投稿BAN/運用分析）を統合した結論：

- **トレンド収集**: TikTok Research APIの日本商用開放は2026年5月時点でも未実現。実務解は **Apify Creative Center Scraper + ScrapTik** または **Bright Data Dataset**。ApifyとScrapTikは2026年に**MCP対応**追加でClaude Code/Cursorから直接呼出し可能。
- **動画中身解析**: **Gemini 3 Flash**（2025/12 GA、$0.50/1M入力）が60秒動画≒$0.01未満で実用ライン本命。大量インデックスは **TwelveLabs Marengo 3.0**（2025/11 GA、日本語91.1%、$0.042/分）。セグメント自動分類は **Pegasus 1.5**（2026/4）。
- **自動投稿**: TikTok Content Posting APIに2026年Duet/Stitch許可・ジオターゲ・写真投稿・Webhookが追加。ただし**予約投稿は依然API未対応**で、ドラフト止め＋人力投稿が業界標準。
- **運用分析**: 2026年4月にInstagramの**3秒スキップ率（Skip Rate）がGraph API正式提供**開始。Reelsクロスポスト再生数も追加。Looker Studio + Gemini で週次レポ自動化が現実解。

### 工程別 AI実用度マトリクス（2026年5月時点）

| 工程 | 実用度 | 主要ボトルネック |
|---|---|---|
| トレンド収集（メタ） | 高 | TikTok公式APIなし、第三者依存・ToSリスク |
| 動画中身解析 | 高 | Gemini 3 Flashで実質解消。高速カット精密検出のみ残課題 |
| 企画・台本生成 | 高 | ブランドボイス調整は人力 |
| 撮影・編集 | 低〜中 | 出演者・現場感は人力必須 |
| 投稿 | 要注意 | TikTok予約投稿API未対応、規約変化 |
| 運用分析・レポート | 高 | 2026/4 Instagram新メトリクス追加で精度UP |
| 改善提案 | 中 | 文化的解釈・戦略判断は人力優位 |

---

## 工程1: トレンドキーワード/ハッシュタグ収集

### TikTok（最優先）

**TikTok Creative Center（無料・ログイン不要）**
広告主向け公式ツール。トレンドハッシュタグ（7/30日・カテゴリ・地域別）、トレンドサウンド、上位広告クリエイティブ、6s視聴率・CTR・CVR・CPA を公開。**公式APIは存在しない**。2026年4月に**Creative Content Library（CCL）適用データへのプログラマティックスクレイピングがToS違反**として明記強化。
- [TikTok Creative Center](https://business-api.tiktok.com/portal)
- [Apify Creative Center Scraper](https://apify.com/doliz/tiktok-creative-center-scraper/api)

**TikTok Research API（公式）— 2026年5月時点でも日本商用利用不可**
対象は米・欧の非営利学術研究者のみ。2026年に機関所属の明確化要件がさらに厳格化、個人開発者の却下率上昇。日本開放は時期未定。
- [TikTok Research API](https://developers.tiktok.com/products/research-api/)
- [Research API FAQ](https://developers.tiktok.com/doc/research-api-faq)
- [SociaVault: Is TikTok API Free? 2026](https://sociavault.com/blog/tiktok-api-free-2026)

**第三者API 比較（2026年5月時点）**

| サービス | 価格 | 主な機能 | 2026年の動き |
|---|---|---|---|
| ScrapTik (RapidAPI) | $0.002/req | ユーザー・投稿・サウンド・検索・トレンド | **MCP対応追加**、AIエージェントから直接呼出 |
| Apify | $0.30/1k投稿、Actor別 | TikTok Scraper / Trending / Hashtag Analytics | **MCP対応追加**、複数Actor共存 |
| Bright Data | Web Unlocker $3/1k req、Dataset $2.5/1k record（200kバンドル$500） | プロキシ + スクレイパー、400M+住宅IP | 引き続き安定性最高 |
| Data365 | 要見積 | TikTok Trends API | リアルタイム・バイラル特化 |

参考: [Apify ScrapTik](https://apify.com/scraptik/tiktok-api) / [Best TikTok Scrapers 2026 (Proxyway)](https://proxyway.com/best/tiktok-scrapers) / [Best TikTok Data APIs 2026 (Netrows)](https://www.netrows.com/blog/best-tiktok-data-apis-2026)

**TikTok特化SaaS**

| ツール | 価格帯 | 強み |
|---|---|---|
| Exolyt | Free〜250〜600EUR/月 | ハッシュタグ・インフルエンサートラッキング |
| Pentos | 約$49/月〜 | トレンドサウンド・バイラルフォーマット早期検知 |
| HypeAuditor | 要見積 | 不正検出、インフルエンサー分析 |
| Sprout Social | エンタープライズ | TikTokソーシャルリスニング |
| Social Insight (User Local) | 国内 | 7SNS横断、生成AIによるXクチコミ分類・要約追加 |
| Tofu Analytics | 国内 | Threads・Bluesky含む全SNS対応 |
| Kamui Tracker | 国内、要問合せ | 日本市場向け |

参考: [SNS分析ツール比較 2026 (LISKUL)](https://liskul.com/sns-analysis-104823)

> **国内補足**: TikTok Shop が2025/6/30 日本ローンチ、2026/2 時点で登録店舗数50,000超（ローンチ時比3倍）。TikTok分析ニーズが国内で急拡大中。

### YouTube Shorts/通常

**YouTube Data API v3（公式・無料枠あり）**
- 無料クォータ: 10,000ユニット/日（検索100ユニット、トレンド `videos.list?chart=mostPopular` は1ユニット）
- **Shorts専用エンドポイントは2026年5月時点も公式未公開**（縦型・60秒以内で自動分類されるのみ、`isShort`フラグなし）
- クォータ増にはCompliance Audit審査が必要
- [YouTube Data API v3 Revision History](https://developers.google.com/youtube/v3/revision_history)

### Instagram Reels

**Instagram Graph API（v21.0）— 2026年4月にメジャー拡張**

2026年4月にMeta公式が大幅拡張を発表（[Social Media Today報道](https://www.socialmediatoday.com/news/meta-expands-instagram-management-apis/818385/)）。

- **3秒スキップ率（Skip Rate）の正式提供** ← 運用代行の本丸メトリクス
- **クロスポスト再生数**: `crossposted_views`・`facebook_views`
- **エンゲージメント拡充**: `reposts_count`・`saved`・`shares`
- **パートナーシップ広告ラベル対応**: サードパーティ投稿時に有料パートナーシップ開示ラベル付与可能
- **Like/Unlike API解禁**: 外部ツールから代行いいねが可能に
- ハッシュタグ検索制限は据え置き（30件/7日）

参考: [Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/) / [Updated Marketing API Metrics](https://storrito.com/resources/how-instagram-marketing-api-metrics-work/)

### X / Threads / Facebook

**X API — 2026年2月に従量課金へ全面移行、4月に大幅改定**

- 2026/2/6: Basic/Pro固定プラン廃止、新規は従量課金のみ。無料プランユーザーには$10クレジット付与
- 2026/4/20改定:
  - Owned reads（自分の投稿・ブックマーク・フォロワー）: **$0.001/req に値下げ**
  - 通常書き込み（URLなし）: $0.010 → **$0.015/req**
  - **URL付き投稿: $0.20/req（+1,900%）** ← 自動拡散系は経済的に成立しない
  - フォロー・いいね・引用ポストはセルフサーブAPIから除外、エンタープライズ限定

参考: [X API Pricing Update April 20 2026 (公式)](https://devcommunity.x.com/t/x-api-pricing-update-owned-reads-now-0-001-other-changes-effective-april-20-2026/263025) / [X Revamps API Pricing (Social Media Today)](https://www.socialmediatoday.com/news/x-formerly-twitter-announces-new-api-pricing-structure-xai/811667/)

---

## 工程2: 伸びている投稿の中身を解析（メタ＋VLM）

### 「ここまで可能 / ここから人力」線引き表（2026年5月時点）

| タスク | 現状AIで可能か | 推奨ツール |
|---|---|---|
| 最初3秒のフック構造分析 | 可能（精度大幅向上） | **Gemini 3 Flash** + プロンプト設計 |
| カット切替検出（秒単位） | 可能 | PySceneDetect + ffmpeg、または Gemini 3 Pro（連続ストリーム推論） |
| テロップ（日本語OCR） | 可能 | TwelveLabs Pegasus 1.5 / Gemini 3 |
| 音声書き起こし（日本語） | 高精度で可能 | Whisper large-v3 / Gemini内蔵ASR |
| BGM検出（曲名特定） | 部分的 | Marengo 3.0 音声理解 + ACRCloud |
| 出演者属性 | 可能（プライバシー注意） | Gemini 3.1 Pro |
| 高速カット（<0.5秒）の精密検出 | 困難だが改善余地あり | Gemini 3 Flash は最大10FPSに対応 |
| 「なぜ伸びたか」の因果解釈 | 不可（相関把握まで） | 人力必須 |
| 戦略提案 | 不可 | 人力 |

### Google Gemini 3 系（コスト・精度の本命）

**Gemini 3 Flash**（2025/12 GA・実用主役）
- 価格: **入力 $0.50/1M、出力 $3.00/1M トークン**
- 動画仕様: **デフォルト1FPS、最大10FPS対応**（高速アクション向け）
- トークン消費: 標準解像度 約300tok/秒、低解像度 約100tok/秒
- 1Mトークンで標準1時間 / 低解像度3時間動画を一括処理
- **60秒Shortsで約18,000トークン ≒ $0.009/本**

**Gemini 3.1 Pro**（2026/2/19 GA・最上位）
- 価格: 入力 $2.00/1M、出力 $12.00/1M（200K超は$4/$18）
- **フレームバイフレームではなくネイティブ動画ストリーム推論** ← 時系列因果の理解が一段上
- ARC-AGI-2 で77.1%

参考: [Gemini 3 Flash公式](https://blog.google/products/gemini/gemini-3-flash/) / [Video Understanding Docs](https://ai.google.dev/gemini-api/docs/video-understanding) / [Gemini 3.1 Pro価格ガイド](https://devtk.ai/en/blog/gemini-3-1-pro-pricing-guide-2026/) / [Artificial Analysis](https://artificialanalysis.ai/models/gemini-3-1-pro-preview)

### OpenAI GPT-5.5（2026/4/23 リリース）

- 価格: $5.00/1M入力、$30.00/1M出力（Pro: $30/$180）
- モダリティ: text + image。**動画ファイル直接入力は非対応または限定的**（フレームサンプリング方式）
- SNS動画解析にはGemini系比でコスパ劣後。本命にはなりえない
- [OpenRouter GPT-5.5](https://openrouter.ai/openai/gpt-5.5) / [apidog 価格](https://apidog.com/blog/gpt-5-5-pricing/)

### Anthropic Claude（Opus 4.7 / Sonnet 4.6 / Haiku 4.5）

- **動画ファイル直接入力は2026/5時点で非対応**
- Files API（files-api-2025-04-14）はPDF・画像・テキストのみ
- 動画解析用途には不向き。文字起こし後のスクリプト分析・企画立案補助で活用
- [Anthropic Files API](https://platform.claude.com/docs/en/build-with-claude/files) / [Claude動画分析解説](https://vomo.ai/blog/can-claude-analyze-video)

### TwelveLabs（動画特化エンジン）

**Marengo 3.0**（2025/11/17 GA、AWS re:Invent 2025/12/1 発表）
- 改良: **最大4時間動画対応**（2.7比2倍）、ストレージ50%削減、インデックス2倍高速
- 日本語: **Crossmodal 3600ベンチで日本語91.1%**（33言語以上、最上位クラス）
- 価格(Developer): **インデックス $0.042/分**、埋め込み $0.0015/分、検索API $4/1k クエリ
- 用途: 大量動画の類似インデックス・セマンティック検索の本命
- [Marengo 3.0公式](https://www.twelvelabs.io/blog/marengo-3-0) / [AWS発表](https://press.aboutamazon.com/aws/2025/12/twelvelabs-launches-its-most-powerful-video-understanding-model-marengo-3-0-on-twelvelabs-and-amazon-bedrock)

**Pegasus 1.5**（2026/4/20 発表、5/6 同期分析エンドポイント対応）
- 新機能: **ビデオセグメンテーション（シーン種別自動分類）**、同期分析エンドポイント、Video OCR
- 価格(Developer): **入力動画 $0.0292/分**、出力テキスト $0.0075/1k トークン
- 用途: SNS動画の「フック / 本編 / CTA」自動分離、構造化テキスト出力
- Pegasus 2.x は2026/5時点で未発表
- [TwelveLabs リリースノート](https://docs.twelvelabs.io/docs/get-started/release-notes) / [Pricing](https://www.twelvelabs.io/pricing)

### オープン系（セルフホスト選択肢）

**Qwen3-VL**（Alibaba、2025/9〜10 段階リリース）
- 規模: 2B/4B/8B/32B（dense）、30B-A3B/235B-A22B（MoE）の6バリアント
- **256Kコンテキスト（最大1Mまで拡張可能）で2時間動画を秒単位検索**
- セルフホスト可、APIコスト不要
- [Qwen3-VL GitHub](https://github.com/QwenLM/Qwen3-VL) / [arXiv](https://arxiv.org/abs/2511.21631)

**InternVL3.5**（2025/8〜）: 78Bでオープン最高水準、長時間動画ベンチ LVBench で評価済。[arXiv](https://arxiv.org/html/2508.18265v1)

### OSS自作パイプライン構成

```
yt-dlp（ダウンロード）
 → ffmpeg（MP4正規化）
 → PySceneDetect 0.7（ショット境界、adaptive detector）
 → Whisper large-v3（日本語ASR、必要時）
 → Gemini 3 Flash（VLM統合プロンプト、最大10FPSで高速カット対応）
 → JSON化 → Notion / Sheets
```

参考: [PySceneDetect](https://github.com/breakthrough/pyscenedetect) / [TikTok Analyzer (kariemoorman)](https://github.com/kariemoorman/tiktok-analyzer)

### SaaS型の動画解析サービス

- **Shortimize**: TikTok/Reels/Shortsの50+カテゴリ日次更新、エージェンシー向け。[Shortimize](https://www.shortimize.com/)
- **Meedro**: 50万本ライブラリ、10言語対応（日本語含む）、フック/ペーシング/CTA/感情トリガー分解。[Meedro](https://meedro.com/)
- **VidIQ**: YouTube専用、MCP対応でClaude/Cursorから直接クエリ。[VidIQ MCP](https://vidiq.com/mcp/)

---

## 工程3: ドラフト生成→人力投稿ワークフロー

### TikTok Content Posting API — 2026年の機能追加

公式投稿API自体は規約違反ではないが、シャドウBANリスクは継続（プログラム的アカウント、同一IP複数アカウント、人間離れした頻度）。2026年に以下が追加：

- **Duet/Stitch許可フラグ** をAPIで指定可能
- **ブランデッドコンテンツ開示フラグ**（2025/9 義務化、API側で対応）
- **ジオターゲティング**（地域別視聴可否）
- **Webhookコールバック**（アップロードステータス非同期通知）
- **写真投稿対応**（動画以外もAPI投稿可）
- ❌ **予約投稿（scheduled_publish_time）は依然API未対応** — Creator Studio留保

→ 「即時公開 or ドラフト保存」の2択。予約を伴う運用は手動 or サードパーティスケジューラ依存。
- [Content Posting API公式](https://developers.tiktok.com/products/content-posting-api/) / [How to Post via API 2026](https://posteverywhere.ai/blog/post-to-tiktok-api)

### Instagram / YouTube / X

- **Instagram Graph API**: 公式投稿OK、Like/Unlike API解禁（2026/4）、パートナーシップ広告ラベルもAPIから付与可能に
- **YouTube Data API v3**: アップロード公式サポート、縦型3分以内で自動Shorts判定。24時間で10本上限、未審査プロジェクトは非公開デフォルト
- **X API**: 2026/4/20改定後、URL付き投稿は$0.20/req で大量投稿は経済的に困難。協調的非本物行為・自動エンゲージメントはBAN対象

### 海外エージェンシー4点チェック

「AI生成 → 4点チェック（ファクト/ボイス/コンプラ/CTA）→ 承認 → 手動スケジュール投稿」が標準。20〜30投稿/週で15→4時間/週へ短縮事例。
- [adpicto Approval Workflow](https://www.adpicto.com/en/blog/social-media-post-approval-workflow-ai) / [trustypost 2026](https://trustypost.ai/blog/social-media-approval-workflow-2026-simple-sops/)

### スケジューラ比較

| ツール | 特徴 | 国内対応 |
|---|---|---|
| SocialBee | AI Copilotで戦略生成、カテゴリ別キュー | ◯ |
| Buffer | シンプルなドラフト＋AIキャプション | ◯ |
| Later | ビジュアルグリッドプレビュー | ◯ |
| Metricool | ドラフト＋分析一体、広告分析強い | ◯ |
| SocialDog（国内） | X/IG/Threads/FB予約、月額1,480円〜 | ◎ |

参考: [Later 2026](https://later.com/blog/social-media-scheduling-tools/) / [Buffer 2026](https://buffer.com/resources/social-media-scheduling-tools/)

---

## 工程4: 運用分析の自動化

### 各プラットフォームの取得可能メトリクス（2026年5月時点）

- **TikTok**: 視聴回数・リーチ・プロフィール訪問・フォロワー増減・シェア・6s視聴率（Creative Center）。**リテンションカーブはネイティブ閲覧可、API取得は限定的**
- **Instagram Reels**: 2026/4から **3秒スキップ率（Skip Rate）正式API提供** ← 大型アップデート。Views（旧Impressions/Plays統合）・リーチ・いいね・保存・コメント・シェア・`ig_reels_avg_watch_time`（ms）・完了率・`crossposted_views`・`facebook_views`・`reposts_count`
- **YouTube**: Watch Time・視聴維持率・インプレッションCTR が Data API v3 で取得可
- **X**: 従量課金移行後、Owned reads は$0.001/req に値下げで自社投稿の分析コストは下がった

参考: [Meta Expands Instagram APIs](https://www.socialmediatoday.com/news/meta-expands-instagram-management-apis/818385/) / [Updated Marketing API Metrics](https://storrito.com/resources/how-instagram-marketing-api-metrics-work/) / [TikTok Retention Benchmarks 2026](https://retensis.com/blog/tiktok-retention-rate-benchmarks-2026)

### Looker Studio + Gemini

- 無料、複数SNS接続、ダッシュボード自動更新
- 2025/6〜 Looker Studio Pro で **Gemini標準搭載**、自然言語クエリ・Python連携可
- マルチクライアント・ホワイトラベルは Swydo / AgencyAnalytics / Whatagraph 優位

参考: [Swydo Connectors](https://www.swydo.com/blog/best-looker-studio-connectors/) / [AgencyAnalytics Looker Review](https://agencyanalytics.com/blog/looker-studio-review)

---

## 結論: 推奨パイプライン（社内向け）

### フェーズ1（即着手・PoC）

**目的**: 「TikTokトレンドハッシュタグ → 上位動画10本のメタ＋VLM解析」の最小スクリプト化

```
Apify Creative Center Scraper（トレンドHT取得）※MCP経由でClaude Codeから直接
 → Apify TikTok Trending Videos（HT別Top動画取得）
 → yt-dlp（動画ダウンロード）
 → Gemini 3 Flash（フック・カット・テロップ・出演者・BGM特徴のVLM解析、必要なら10FPS）
 → Notion DB or Google Sheets（結果保存）
```

Claude Code で1スクリプト化。**100本/週解析でGemini側コスト ≒ $1/週**（Gemini 3 Flashで60秒動画≒$0.009/本）。Apifyは別途従量。

### フェーズ2（投稿運用）

- 投稿は**手動継続**（TikTok APIは予約投稿未対応、リーチ低下リスクも残る）
- AI生成ドラフトはNotion集約、4点チェックフローで承認後に手動投稿
- 海外人力投稿への引き渡しもNotion経由

### フェーズ3（運用分析）

- Instagram Reels の **3秒スキップ率API（2026/4正式提供）** を取り込み、フックの改善ループに即活用
- Insightsを Looker Studio + コネクタへ接続、Gemini で週次レポ半自動化
- マルチクライアント化段階で Swydo / AgencyAnalytics 検討

### 受講生横展開時の注意

- TikTok Research APIの商用・地域制限を明示（2026/5時点も日本不可）
- Apify/ScrapTik等の非公式利用時のToSリスク（2026/4 CCLスクレイピング規約違反明記）をセット説明
- 「投稿はドラフト止め」を初期教材から固定

---

## 未解決・要追加検証

- TikTok API経由投稿のリーチ低下を示す**実証データ**（公式・第三者ともに未確認のまま）
- TwelveLabs Pegasus 1.5 の**日本語テロップOCR精度**の実測（Marengo 3.0は日本語91.1%確認済み）
- Kamui Tracker / Tofu Analytics の料金詳細（要直接問合せ）
- Meedroが「動画中身を実際にVLMで解析しているか／メタベースか」の実態
- Gemini 3 Flash の最大10FPS設定での**高速カット（<0.5秒）見落とし率**実測

---

## 参考URL（統合・2026/5時点）

### モデル・VLM
- [Gemini 3 Flash 公式（2025/12）](https://blog.google/products/gemini/gemini-3-flash/)
- [Gemini Video Understanding Docs](https://ai.google.dev/gemini-api/docs/video-understanding)
- [Gemini 3.1 Pro 価格ガイド 2026](https://devtk.ai/en/blog/gemini-3-1-pro-pricing-guide-2026/)
- [Gemini 3.1 Pro Preview (Artificial Analysis)](https://artificialanalysis.ai/models/gemini-3-1-pro-preview)
- [OpenRouter GPT-5.5](https://openrouter.ai/openai/gpt-5.5) / [apidog GPT-5.5 価格](https://apidog.com/blog/gpt-5-5-pricing/)
- [Anthropic Files API](https://platform.claude.com/docs/en/build-with-claude/files) / [Claude動画分析解説](https://vomo.ai/blog/can-claude-analyze-video)
- [TwelveLabs Marengo 3.0 ブログ](https://www.twelvelabs.io/blog/marengo-3-0) / [AWS Marengo 3.0発表](https://press.aboutamazon.com/aws/2025/12/twelvelabs-launches-its-most-powerful-video-understanding-model-marengo-3-0-on-twelvelabs-and-amazon-bedrock)
- [TwelveLabs リリースノート](https://docs.twelvelabs.io/docs/get-started/release-notes) / [Pricing](https://www.twelvelabs.io/pricing)
- [Qwen3-VL GitHub](https://github.com/QwenLM/Qwen3-VL) / [Qwen3-VL arXiv](https://arxiv.org/abs/2511.21631)
- [InternVL3.5 arXiv](https://arxiv.org/html/2508.18265v1)

### トレンド収集・SNS API
- [TikTok Creative Center](https://business-api.tiktok.com/portal)
- [TikTok Research API](https://developers.tiktok.com/products/research-api/) / [FAQ](https://developers.tiktok.com/doc/research-api-faq) / [SociaVault TikTok API Free 2026](https://sociavault.com/blog/tiktok-api-free-2026)
- [TikTok Content Posting API](https://developers.tiktok.com/products/content-posting-api/) / [Post to TikTok via API 2026](https://posteverywhere.ai/blog/post-to-tiktok-api)
- [Apify ScrapTik](https://apify.com/scraptik/tiktok-api) / [Best TikTok Scrapers 2026](https://proxyway.com/best/tiktok-scrapers) / [Best TikTok Data APIs 2026](https://www.netrows.com/blog/best-tiktok-data-apis-2026)
- [Bright Data TikTok Dataset](https://brightdata.com/products/datasets/tiktok)
- [Data365 TikTok Trends](https://data365.co/blog/tiktok-trends-api)
- [Meta Expands Instagram APIs 2026/4](https://www.socialmediatoday.com/news/meta-expands-instagram-management-apis/818385/)
- [Instagram Media Insights](https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/) / [Updated Marketing API Metrics](https://storrito.com/resources/how-instagram-marketing-api-metrics-work/)
- [YouTube Data API v3 Revision History](https://developers.google.com/youtube/v3/revision_history)
- [X API Pricing Update 2026/4 (公式)](https://devcommunity.x.com/t/x-api-pricing-update-owned-reads-now-0-001-other-changes-effective-april-20-2026/263025) / [X Revamps API Pricing](https://www.socialmediatoday.com/news/x-formerly-twitter-announces-new-api-pricing-structure-xai/811667/)

### ワークフロー・スケジューラ・分析
- [AI Approval Workflow (adpicto)](https://www.adpicto.com/en/blog/social-media-post-approval-workflow-ai) / [Approval Workflow 2026 (trustypost)](https://trustypost.ai/blog/social-media-approval-workflow-2026-simple-sops/)
- [Later Scheduling 2026](https://later.com/blog/social-media-scheduling-tools/) / [Buffer 2026](https://buffer.com/resources/social-media-scheduling-tools/)
- [Swydo Looker Connectors](https://www.swydo.com/blog/best-looker-studio-connectors/) / [AgencyAnalytics Looker Review](https://agencyanalytics.com/blog/looker-studio-review)
- [TikTok Retention Benchmarks 2026](https://retensis.com/blog/tiktok-retention-rate-benchmarks-2026)
- [SNS分析ツール比較 2026 (LISKUL)](https://liskul.com/sns-analysis-104823) / [SNSニュース 2026/5 (Comnico)](https://www.comnico.jp/we-love-social/sns-news)
- [Shortimize](https://www.shortimize.com/) / [Meedro](https://meedro.com/) / [VidIQ MCP](https://vidiq.com/mcp/)
