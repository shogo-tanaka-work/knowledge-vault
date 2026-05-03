# Email Security (Cloudflare One)

> 注：本記事の Email Security はクラウド型のメールセキュリティ製品（旧 Area 1 Security）であり、独自ドメインのメール転送サービスである **Cloudflare Email Routing**（Tier 4 で扱う予定）とは別物である。前者はフィッシング・BEC・マルウェアからメール受信箱を守るセキュリティ製品、後者はゾーン宛メールを任意の宛先に転送するルーティング機能である。

## 一行サマリ
Microsoft 365 / Google Workspace を中心とした既存メール環境の前段または並走として動作し、AI とグローバル脅威インテリジェンスでフィッシング・BEC・マルウェア・添付ファイル攻撃を配信前または配信後に検出・隔離するクラウド型メールセキュリティサービスである。

## 解決する課題（Why）
従来型のセキュアメールゲートウェイ（SEG）は MX を切り替える前段プロキシとして機能してきたが、近年は Microsoft 365 / Google Workspace 標準のフィルタを通り抜ける高度なフィッシング・BEC が増え、SEG だけでは取り切れない領域が広がっている。Cloudflare Email Security は次の課題を解く。

- **BEC（Business Email Compromise）**：実在する取引先・経営層を装った請求書すり替え・偽送金指示など、添付もリンクもない純粋な「文面詐欺」を、文脈解析と送信者の通信パターン学習で検知する。
- **フィッシング**：URL レピュテーション・ドメイン類似度・ペイロードのレンダリング解析を組合せ、配信前にリンクを評価する。検知率は公称 99.99% を謳う。
- **添付マルウェア**：サンドボックスで添付を実行・解析し、ゼロデイ／回避型マルウェアも検知する。
- **配信前検出と配信後修復の両立**：MX 切替で配信前にブロックするだけでなく、API 連携で配信後の受信箱からも遡って隔離（Auto Move）できる。
- **DMARC 運用負荷**：DMARC レポートの集計・可視化・なりすまし送信の調査をダッシュボードで行える。

## 主要機能（What）

### Pre-delivery vs Post-delivery
- **Pre-delivery（MX/Inline デプロイ）**：MX レコードを Cloudflare に向け、すべての受信メールが Cloudflare 経由で受信箱に届くようにする。スコア判定によりブロック・隔離・タグ付け・本文書き換え（リンク書き換え、警告バナー追加）まで配信前に行える。リアルタイム保護が可能で、悪性メールはユーザーの目に触れない。
- **Post-delivery（API デプロイ）**：MX は変更せず、Microsoft Graph API または Google Workspace API 経由で受信箱を監視し、配信済みメールをスキャンする。誤検知時の影響が少なく、導入時の MX 変更による事故リスクがない一方、ユーザーが受信箱で一瞬目にする可能性がある（後述の Auto Move で隔離）。

実運用では「**MX で前段ブロック + API で並走チェックして遅延検知分も後追い隔離**」というハイブリッド構成が推奨される。

### MX デプロイ
他社 SEG と同じ「MX 切替型」の動作モード。すべてのメールを Cloudflare のエッジで受け、判定後にダウンストリームの Microsoft 365 / Google Workspace / Exchange Online / オンプレ Exchange / 他社メール基盤に転送する。Microsoft 365・Google Workspace に限らず任意のメール基盤に対応する。

### API デプロイ
- **Microsoft 365**：Microsoft Graph API 経由でテナントに接続し、受信箱を直接監視・操作する。MX 変更は不要。
- **Google Workspace**：Google Workspace API（および BCC / Journaling）でメッセージコピーを取得しスキャンする。
- ディレクトリ同期（ユーザー・グループ）が API 連携で行え、ポリシーの宛先指定がしやすい。

### Auto Move
API デプロイの中核機能。Cloudflare の判定結果（disposition：MALICIOUS / SUSPICIOUS / SPAM / SPOOF / BULK 等）に基づき、受信箱に配信されたメールを自動的に隔離フォルダ・迷惑メール・ゴミ箱へ移動する。判定が後から変わった場合（脅威インテリジェンス更新による再評価）にも遡って受信箱から取り下げる。Microsoft 365 / Google Workspace の双方で利用できる。

### Link Isolation（RBI 連携）
Email Security はメール内の URL を書き換え、クリック時にもう一度 URL レピュテーションを評価する（Time-of-click protection）。さらに **Cloudflare Browser Isolation** と統合し、疑わしいリンクをユーザーのブラウザに直接届けず、リモートブラウザ内で隔離して描画できる。資格情報窃取ページに対する入力ブロックなどもここで効く。詳細は Browser Isolation 記事を参照。

### DMARC Management
DMARC / SPF / DKIM のレポート集約とドメインなりすましの可視化、設定不備の検出を提供する。SEG と DMARC 管理ツールを別々に契約していた組織は統合できる。

### マルチチャネル拡張
メール以外に Slack / Microsoft Teams / SMS / QR コード経由のフィッシングまで対象を広げる方向に進化している（プランによる）。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- Microsoft 365 / Google Workspace を採用しており、標準フィルタ（EOP / Defender P1）を通り抜けるフィッシング・BEC を取りこぼしている組織。
- 既存 SEG（Proofpoint / Mimecast）からのリプレース。とくに価格と運用負荷の観点で見直したいケース。
- Cloudflare One 全体（Access / Gateway / CASB / Browser Isolation）を採用しており、URL のクリック後挙動まで含めて統一ポリシーで守りたいケース。
- 配信後修復（Auto Move）を即日入れたい場合。MX 変更を伴わないため導入が早い。
- DMARC 運用を内製で抱えており、ツール統合したい組織。

### 適していないシーン
- メール基盤がオンプレ Exchange のみで、API 連携機構が弱い古い環境。MX デプロイは可能だが、Auto Move 等の旨みは API 連携前提である。
- 高度な DLP・暗号化メール（S/MIME 強制、PGP 鍵管理）まで含む包括的なメッセージング基盤の置き換えを目的とする場合。Email Security はインバウンド保護に重心がある。
- 既に Microsoft Defender for Office 365 P2 でほぼ満足しており、追加コストの正当化が難しい組織。
- Cloudflare アカウントを持たない・Cloudflare 全体への投資意向がない組織（単独製品としても買えるが、エコシステム統合が最大の差別化要因のため）。

## 競合・代替

| 観点 | Cloudflare Email Security | Proofpoint | Abnormal Security | Microsoft Defender for Office 365 | Mimecast |
|---|---|---|---|---|---|
| デプロイ形態 | MX / API（M365・Google） | MX 中心、API も対応 | API 専業（M365・Google） | M365 ネイティブ | MX 中心 |
| Pre-delivery 検出 | 強い（MX/Inline） | 強い（老舗 SEG） | なし（API のみ） | M365 内で動く | 強い |
| Post-delivery 修復 | Auto Move | あり | 中核機能 | あり（ZAP） | 限定的 |
| BEC 検出アプローチ | AI＋脅威インテリ＋通信パターン | ルール＋AI | 行動分析特化（ML） | Defender ML | ルール＋AI |
| Cloudflare One 統合 | 完全統合（Browser Isolation・Gateway） | なし | なし | Microsoft 365 内統合 | なし |
| 強み | 価格・統合・99.99% を謳う検知率 | 機能網羅性・大企業導入実績 | BEC の検知精度に定評 | M365 とのネイティブ統合・追加コスト最小 | アーカイブ・継続性に強い |
| 弱み | DLP・アーカイブは別領域 | 価格・UI の重さ | Pre-delivery を持たない | Microsoft 単一ベンダーリスク | UI と AI 検知精度で後発に押される |

Abnormal Security は API 専業の比較対象としてよく挙がる。Cloudflare Email Security は「MX も API も両方できる」点と「Browser Isolation との時刻クリック保護統合」が独自性となる。

## 料金
旧 Area 1 ライセンスを引き継ぎ、現在は **Cloudflare Zero Trust（Cloudflare One）の Enterprise プラン**として提供される。

- 単独製品としての契約と、Cloudflare One スイートにバンドルした契約の双方が可能である。
- 公開料金表は提供されておらず、ユーザー数・受信メールボリューム・追加オプション（PhishGuard マネージドサービス、Browser Isolation 統合、DLP）に応じた個別見積もりとなる。
- 参考価格帯：1 ユーザーあたり月額数ドル〜 USD 二桁前半が一般的なレンジ（公式公表値ではなく、競合 SEG と同等帯）。
- **PhishGuard**：Cloudflare のセキュリティアナリストが顧客テナントを監視・脅威ハンティングを代行するマネージドアドオン。中堅企業で SOC 機能が薄い場合の選択肢。
- Free / Pay-as-you-go プランは存在しない。Access や Gateway と異なり「無料 50 ユーザー」のような枠はない点に注意。

## CLI / IaC 操作例
本機能は Cloudflare ダッシュボード（Zero Trust → Email Security）からの操作が中心であり、Terraform Provider にもまだ専用の `cloudflare_email_security_*` リソースは整備されていない（v5 時点）。API 連携と直接 REST API 呼び出しが現実解である。

### 管理コンソールフロー（Microsoft 365 / API デプロイ）
```
1. Zero Trust ダッシュボード → Email Security → Settings → Domains
2. 「Add domain」で保護対象ドメインを登録
3. 「Connect Microsoft 365」を選び、グローバル管理者アカウントで OAuth 認可
   - Microsoft Graph に対するメールスキャン権限を付与
4. ディレクトリ同期（ユーザー・グループ）が自動で開始される
5. Detection settings で disposition ごとの自動アクション（Auto Move 先）を設定
   - MALICIOUS → Junk Email
   - SUSPICIOUS → Quarantine フォルダ
   - SPOOF → タグ付けのみ など
6. Impersonation Registry に保護対象の役員・取引先ドメインを登録
7. 数日のラーニング期間後にエンフォースモードへ切替
```

### Google Workspace（API デプロイ）
```
1. Google Workspace 管理コンソールでサービスアカウントとドメイン全体委任を設定
2. Cloudflare 側に JSON キーをアップロード、または OAuth 連携を実施
3. Gmail API のスコープ（gmail.modify 相当）を委任
4. 以降の運用は M365 と同様
```

### MX デプロイ（共通）
```
1. Cloudflare 側で受信用ホスト名（mailstream-*.cloudflare.net 系）を発行
2. 自社ドメインの MX レコードを Cloudflare 提供ホストに変更
3. ダウンストリーム（M365 / Google Workspace）の受信制限で
   Cloudflare 由来の IP レンジのみ許可するようインバウンドコネクタを設定
4. SPF に Cloudflare のインクルードを追加
```

### REST API 例（Detection settings 取得）
```bash
curl -H "Authorization: Bearer $CF_API_TOKEN" \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/email-security/settings/detections"
```

将来的に Terraform リソースが追加された場合は IaC 化を再検討するとよい。当面はテナント設定をスクリプト化（API 経由）して GitOps 的に管理するのが現実解である。

## 制限・注意点
- **Terraform 対応が薄い**：Access や Tunnel と異なり、IaC 化の選択肢が限定的である。設定はダッシュボード／API での管理が前提となる。
- **Auto Move は API デプロイ前提**：MX デプロイ単独では「配信前ブロック」しかできない。配信後の遡及隔離が欲しいなら API 連携を併設する必要がある。
- **ディレクトリ同期の権限**：Microsoft Graph や Google Workspace API への強い権限を Cloudflare に渡す。最小権限で済むかをセキュリティチームと事前にレビューすること。
- **MX デプロイ時のフェイルオープン挙動**：上流障害の波及を避ける設計だが、可用性 SLO はメール基盤本体（M365 / Google）と Cloudflare の双方を見て評価する必要がある。
- **誤検知運用**：BEC 系の AI 判定は文面文脈に依存するため、初期は学習期間として monitor モードで運用し、業務メール（社内通称、略語、外部協力会社の独特な署名）に合わせてチューニングが必要である。
- **DLP・暗号化送信**：本製品は受信側保護が中心であり、送信メールの DLP・暗号化（PGP / S/MIME）は別領域である。Cloudflare Data Loss Prevention や他社製品との組合せが必要となる。
- **Cloudflare Email Routing と混同しない**：契約・課金・管理画面が別系統である。
- **Free 枠なし**：Cloudflare One の他コンポーネントと違い、本機能は商用契約前提で評価期間（PoC）以外で無料利用はできない。

## 参考リンク
- Email Security 概要：https://developers.cloudflare.com/cloudflare-one/email-security/
- 製品ページ（マーケティング）：https://www.cloudflare.com/zero-trust/products/email-security/
- 旧 Area 1 ドキュメント：https://developers.cloudflare.com/email-security/
- Cloudflare One llms.txt：https://developers.cloudflare.com/cloudflare-one/llms.txt
- Browser Isolation（リンク隔離連携の文脈）：https://developers.cloudflare.com/cloudflare-one/policies/browser-isolation/

---
参照日: 2026-05-03
