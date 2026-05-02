# Supabase × 医療システム設計 QAまとめ

作成日: 2026-05-02  
対象: 医療クリニック向けSaaS（電子カルテ・薬品在庫・予約管理等）

---

## 背景・用途

クリニック向けシステム提案時に整理したQAリストをナレッジ化。  
Supabaseのアーキテクチャ設計から日本の医療コンプライアンス対応まで、医療系SaaS構築に汎用的に使える知見をまとめた。

---

## A. アーキテクチャ設計方針

### プロジェクト構成

**推奨: 1 Supabase Project + 共通DB + clinic_id + RLS**

- 小〜中規模アプリでは、複数プロジェクト構成より1プロジェクト内マルチテナントの方が開発・運用・AI連携・管理画面がシンプル
- 有料プラン前提で、PITR/バックアップ/ログ/接続上限/ストレージを初期から見積もる
- プロジェクト分離に移行する判断基準: 完全分離・個別バックアップ・個別SLA・大規模院のリソース分離が必要になったとき

### マルチテナント設計

**推奨: shared schema + clinic_id + RLS**

```sql
-- 全テナントデータテーブルに clinic_id を必須で持たせる
-- RLSで「自分が所属する clinic_id のデータのみ」を許可
```

- スキーマ分離はクリニック増加時のマイグレーション・横断集計・保守が重くなる
- プロジェクト分離は最も分離度が高いが、Auth/Storage/Functions/Secrets/費用管理が増えるため初期は不採用

### トランザクション設計

| 処理の性質 | 実装方式 |
|---|---|
| 単純CRUD（一覧取得、基本情報更新） | Supabase Client + RLS |
| ACID必要な業務処理（予約確定・処方確定・在庫減算） | Postgres関数/RPC（1トランザクション） |
| 外部API連携・秘密鍵・複雑検証・通知 | Edge Functions → 単一RPC呼び出し |
| アプリ側で複数クエリを順番に投げる | **原則禁止**（途中失敗・二重送信・ロールバック漏れリスク） |

- Edge Functionsで複数のSupabase APIを順番に呼ぶだけでは1トランザクションにならない点に注意
- RPCはmigration内でSQL管理、関数名・コメント・型定義・テストを整備する

### Realtime（複数端末同期）

- 有料プラン前提なら受付＋診察端末の同期はRealtimeで対応可能
- 医療データ本文を過剰に流さず、IDやステータス変更を中心にする
- 端末数×タブ数×チャンネル数で接続数を見積もる（Pricing/Realtime Limitsを都度確認）

---

## B. 独自ドメイン・インフラ

- **クリニック向けWebサイト独自ドメイン**: フロントホスティング（Vercel/Cloudflare Pages）に向ける
- **Supabase Custom Domain**: Supabase API/Auth URLを独自ドメイン化する有料アドオン。初期は不要
- Custom Domainが必要になるケース: OAuth同意画面・外部連携API・QRコード・メール内URLでSupabase URLが表に出る場合
- フロントホスティング: Vercel/Cloudflare Pages/Netlifyを第一候補（GitOps・CDN・プレビューデプロイ・ロールバック対応）

---

## C. セキュリティ・医療コンプライアンス

### 3省2ガイドライン

日本の医療機関で患者情報をクラウドに置く際の主な根拠：

1. **個人情報保護法** - 病歴等は要配慮個人情報。取得に原則本人同意が必要。漏えい時は個人情報保護委員会への報告・本人通知義務
2. **厚労省「医療情報システムの安全管理に関するガイドライン 第6.0版」（令和5年5月）** - 経営管理編/企画管理編/システム運用編/概説編の4編構成
3. **経産省・総務省「医療情報を取り扱う情報システム・サービスの提供事業者における安全管理ガイドライン 第2.0版」（令和7年3月）**
4. **医療法施行規則第14条第2項** - 医療機関の管理者にサイバーセキュリティ確保措置が法令上義務付け

#### Supabase × 個情法の論点

- Supabase = Supabase Pte. Ltd.（シンガポール法人）
- Tokyoリージョン（ap-northeast-1）選択だけで「日本国内サーバー」要件を満たすわけではない
- 個情法28条「外国にある第三者への提供」または法23条「外的環境の把握」のいずれかに該当しうる
- 契約主体・サブプロセッサー（AWS等）・サポート対応国の整理が必要

### e-文書法（電子カルテの三原則）

電子カルテ・診療録を電子保存する場合、以下を満たすシステムと運用が必要：

| 要件 | 内容 | Supabaseでの実装例 |
|---|---|---|
| **真正性** | 入力者の識別と認証 | MFA必須、supa_audit/pgauditで変更履歴記録 |
| **見読性** | いつでも読める状態 | 可用性設計、RTO/RPO定義 |
| **保存性** | 指定期間の保存 | PITR、診療録は患者最終来院から5年保存、Log Drains外部転送 |

### ゼロトラストアーキテクチャ

**ガイドライン第6.0版の正確な解釈:**

> 「ゼロトラスト思考に基づく対策を**必須としているわけではなく**、リスク分析の結果や、費用対効果も考慮したうえで判断することが望ましい」

→「境界防御を捨ててゼロトラストへ」ではなく「境界防御をしっかり固めた上で、ゼロトラストを段階的に取り入れる」が正しい読み方

**小〜中規模クリニックの優先実装（境界防御）:**
- Supabase Network Restrictions（IP allowlist）
- SSL Enforcement
- 管理ダッシュボードへの2FA必須化
- service_role key/secret keyのサーバー側限定
- Cloudflare等のWAF/CDN（フロント側）

**中長期で段階導入（ゼロトラスト要素）:**
- 端末認証、SIEM、SOC、常時セッション検証

### HIPAA

**日本の医療機関には原則対象外。**

- HIPAAは「患者の国籍」ではなく「米国のCovered Entity（医療機関・健康保険）か」で適用
- 日本国内のクリニックは患者が日本人・在日外国人でも、HIPAAの直接適用対象外
- 「慣習的にHIPAAを使う前提」も日本市場では成立しない
- SupabaseのHIPAA BAA締結にはTeam Plan以上 + HIPAA add-on申請が必要（Pro Planでは不可）

### 監査ログ設計

「医療グレード」と断定せず、要件→実装策→ギャップ整理の順で提案する：

| 種別 | 実装方法 | 制約 |
|---|---|---|
| 変更履歴 | supa_audit（トリガー方式） | 書込3k ops/sec超えるテーブルには不向き |
| 閲覧ログ | pgaudit | `pgaudit.log_parameter` はSupabase Hosted版で変更不可（SELECTバインド値の詳細ログに限界） |
| 長期保管 | Log Drains → S3/BigQuery等 | Logs Explorerの保持はプラン依存（医療系の数年〜十数年保管には外部転送が必要） |
| 重要業務 | RPC/Edge Functions内で明示的に監査ログを書き込む | - |

### バックアップ（PITR）

- **PITR利用要件**: Pro Plan以上 + **Small compute add-on以上（Microでは不可）**
- PITR有効時は日次バックアップが置き換わる
- プラン別の日次バックアップ保持期間: Pro 7日 / Team 14日 / Enterprise 最大30日
- **医療系推奨ライン**: RPO=数分単位、RTO=数時間レベル
- 本番投入前にステージングで復元手順をリハーサルする

---

## D. 運用・コスト

### Supabaseプラン選択指針

| 構成 | 月額目安 | 用途 |
|---|---|---|
| Pro $25 + Small compute $15 + PITR 7日 $100 | **約$140/月** | 日本案件3省2ガイドライン適合・本番最小構成 |
| Team $599 + Small compute $15 + PITR $100 + HIPAA add-on（要問合せ） | **約$1,000〜1,500/月** | HIPAA対応が必要な場合 |

**Team Planへの移行判断基準:**
- SOC 2 / ISO 27001の監査証跡が顧客（医療機関・監査人）から要求されたとき
- SSO / SAMLが必要なとき
- Platform Audit Logs、28日ログ保持が要件化されたとき
- HIPAA add-onが必要なとき

Team Planはユーザー数無制限・最低人数制限なし。公式pricingはBeta表記のため契約時に再確認必須。

### 可用性・障害対応

- 医療系では「SaaS障害ゼロ」を前提にしない
- 当日患者リストの定期エクスポート・キャッシュを検討
- RTO/RPO・障害時連絡先・復旧判断者を事前に決める

---

## E. ローカル開発環境（Windows前提）

### Docker・WSL不要の最小構成セットアップ

```powershell
# Step1: Git for Windows をインストール（git-scm.com）→ "Add Git to PATH" チェック
# Step2: Node.js 20+ をインストール（nodejs.org または winget install OpenJS.NodeJS）
# Step3: Scoop を導入
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
iwr -useb get.scoop.sh | iex

# Step4: Supabase CLI を Scoop 経由でインストール（公式推奨・npm global は非サポート）
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase

# Step5: Claude Code ネイティブインストーラ（管理者権限不要）
irm https://claude.ai/install.ps1 | iex

# Step6: プロジェクトに接続
supabase login  # ブラウザOAuth認証
supabase link --project-ref <staging-ref>
supabase gen types typescript --linked > src/types/database.ts
```

**注意:**
- Scoop が社内ポリシーで使えない場合: GitHub Releases から standalone binary をダウンロード → PATH に追加
- アンチウイルスが Claude Code バイナリを誤検知する場合: `~\.local\bin\claude.exe` を例外リストに追加
- 改行コードは LF 統一（`.gitattributes` に `* text=auto eol=lf`, `*.sql text eol=lf`）

### 2環境構成

| 環境 | 用途 | AI操作 |
|---|---|---|
| ステージングProject | 開発用（架空・匿名化データのみ） | 読み書き・破壊的操作・ALTER TABLE直生成OK |
| 本番Project | 実運用（実患者データ） | Claude Codeを**直接接続しない** |

### 本番反映の4ステップ

1. ステージングで試作（Studio or Claude Code経由でフリーに変更）
2. 確定したスキーマを `supabase db pull --linked` か手書きでmigrationファイル化、PRレビュー
3. リセット済みステージングに `db push` でリハ。アプリの主要動線確認
4. 本番に `db push`（リード担当 or CI経由）+ 切り戻し手順を事前に用意

**切り戻し手順の最低ライン:**
- PRにこのmigrationが何を変えたか明記
- ロールバック用の逆SQLを用意
- 本番適用前にPITRの復元ポイントを確認

---

## F. Claude Code × Supabase 連携

### CLI vs MCP 選択指針

**推奨: CLI（Git Bash経由）を基本、MCPは補助**

| 観点 | CLI | MCP |
|---|---|---|
| コンテキスト消費 | ほぼゼロ | 10〜15k tokens / メッセージ（200kウィンドウの5〜10%） |
| 操作範囲 | CLI全機能（db pull/push/diff/dump/migration/gen types等） | MCP公開ツールに限定 |
| UNIXツール連携 | Git Bash付属のgrep/sed/awk/jqとシームレスに連携 | 別途bash必要 |

**MCPを使う場面:**
- テーブル一覧を見せる等の探索的操作
- Linear/GitHub等の他MCPと横断ワークフローを組む場合
- 使う場合は最小スコープで: `?project_ref=<id>&read_only=true&features=database,docs`

### 安全原則（CLI・MCP共通）

1. 接続先はステージングProjectのみ。本番には直接つながない
2. 破壊系コマンド（DROP TABLE/TRUNCATE/db reset/migration repair --status reverted等）は人間が確認してから実行
3. service_role keyはClaude Code環境に置かない（個人OAuth/PATで認証）
4. AI生成SQLは必ずmigrationファイル化 + PRレビューを通す
5. SUPABASE_ACCESS_TOKENは環境変数（`.env` gitignore済み）で管理

### AIにDB定義を渡す際の方針

| 渡してよいもの | 制限 |
|---|---|
| スキーマ（テーブル定義、型情報） | テーブル名にクリニック固有情報がある場合は配慮 |
| 架空・匿名化データのステージングDB | - |
| 行データ | **絶対に渡さない**（要配慮個人情報） |

**Claude Codeの契約階層と保持:**
- Pro/Max個人: 「Improve Claude」OFFで訓練対象外・30日保持
- API/Team/Enterprise: デフォルトで訓練対象外・7日保持
- ZDR契約: リアルタイム廃棄に近い扱い（医療・金融等の強い秘匿要件向け）

---

## G. セキュリティの落とし穴

### RLS未設定リスク

- 全テーブルでRLS有効化を原則にする
- 患者/予約/処方/会計などクリニック別データはclinic_id条件を必須化
- テストユーザーA/Bで「別クリニックのデータが読めない・書けない」自動テストを作る
- Security Advisor警告ゼロを本番リリース条件にする

### APIキー管理

| キー種別 | 利用場所 |
|---|---|
| anon key（公開可能） | フロントエンド。安全性はRLS設計に依存 |
| service_role key | **サーバー側限定**。フロント・Git・AIプロンプトに絶対に出さない |

### 接続数・Supavisor

- サーバーレス環境・Edge Functions・バッチ処理が増えるとDB接続数が膨らむ
- Supavisor/接続プーリング、N+1クエリ対策、不要なRealtime購読削減で対処

---

## 参考文献・ガイドライン

### 厚労省 医療情報システムの安全管理に関するガイドライン 第6.0版（令和5年5月）

4編構成（概説編 / 経営管理編 / 企画管理編 / システム運用編）

| 資料 | URL |
|---|---|
| ガイドライン掲載ページ（第6.0版） | https://www.mhlw.go.jp/stf/shingi/0000516275_00006.html |
| システム運用編 PDF | https://www.mhlw.go.jp/content/10808000/001582980.pdf |
| ガイドライン Q&A（令和7年5月版） | https://www.mhlw.go.jp/content/10808000/001145860.pdf |
| 概要スライド PDF | https://www.mhlw.go.jp/content/10808000/001024389.pdf |

**主要な改定ポイント（第5版からの変更）:**
1. 経営層の責務の明確化
2. ゼロトラストアーキテクチャの導入（ただし必須ではなく段階導入を許容）
3. クラウドサービス利用の具体的要件化
4. 外部委託先管理の強化（責任分界点の契約段階での定義）

**2027年度以降の義務要件:** 新規導入または更新する医療情報システムへの**二要素認証**の採用

### 経産省・総務省 ガイドライン

| 資料 | URL |
|---|---|
| 経産省 事業者向けガイドライン（第2.0版・令和7年3月） | https://www.meti.go.jp/policy/mono_info_service/healthcare/teikyoujigyousyagl.html |

### 個人情報保護委員会

| 資料 | URL |
|---|---|
| 医療・介護関係事業者ガイダンス | https://www.ppc.go.jp/personalinfo/legal/iryoukaigo_guidance/ |
| 個人情報保護委員会 | https://www.ppc.go.jp/ |

### 解説記事・参考

| 資料 | URL |
|---|---|
| TXOne Networks - ガイドライン第6.0版 改定ポイント解説 | https://www.txone.com/ja/blog-ja/guidelines-for-the-security-management-of-healthcare-information-systems-in-ver6/ |
| TrustLogin - 2026年度 二要素認証・保守回線対策 | https://blog.trustlogin.com/2026/medicalinformationguidelines6 |

### Supabase公式ドキュメント（医療系で参照が多い）

- [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [HIPAA Compliance](https://supabase.com/docs/guides/security/hipaa-compliance)
- [Shared Responsibility Model](https://supabase.com/docs/guides/deployment/shared-responsibility-model)
- [pgaudit](https://supabase.com/docs/guides/database/extensions/pgaudit)
- [Backups / PITR](https://supabase.com/docs/guides/platform/backups)
- [Production Checklist](https://supabase.com/docs/guides/deployment/going-into-prod)
- [Windows CLI Getting Started](https://supabase.com/docs/guides/local-development/cli/getting-started)

---

## キーワード（検索・参照用）

- 3省2ガイドライン（厚労省・経産省・総務省）
- 医療情報システムの安全管理に関するガイドライン 第6.0版
- e-文書法（真正性・見読性・保存性）
- 医療法施行規則第14条
- ゼロトラストアーキテクチャ（医療機関向け・段階導入）
- Supabase RLS（Row Level Security）マルチテナント
- clinic_id によるテナント分離設計
- 二要素認証（令和9年度以降の義務要件）
- サービス仕様適合開示書（2省ガイドライン）
- supa_audit / pgaudit
- PITR（Point In Time Recovery）Small compute必須
