# Cloudflare DNS移行 × Workerプロキシ戦略 検証ログ

> ステータス: 進行中
> 作成日: 2026/04/07
> 最終更新: 2026/04/07
> ファイルパス: ~/Documents/verification-logs/projects/20260407_cloudflare-dns-worker-proxy.md

---

📋 プロジェクト概要
* カテゴリ: インフラ設計 / Cloudflare / DNS / プロキシ戦略
* 期間: 2026/04/07 -（検証中）
* 主要メンバー: 田中省伍（shogoworks）
* ステークホルダー: Bytech受講生、個人事業クライアント
* プロジェクトステータス: 進行中

---

## 1. 背景と目的

* `shogoworks.com` ですでにCloudflare運用の実績あり（Google Workspace連携・Worker設定済み）
* 新たな要件として「WordPressで動いているドメインの `/blog` パスだけをVercelの静的サイトに向けたい」という構成を検討
* 同一ドメインで複数サービスを共存させるプロキシ戦略の知見を、Bytech講座コンテンツ・個人発信・クライアント提案に転用することが目的
* 「なぜDNSだけでは振り分けできないのか」という概念的な理解の整理も兼ねる

---

## 2. 取り組み内容

### 実施した施策・活動

* DNS基礎の棚卸し：Aレコード / CNAME / MX / TXT / NS / CAAの役割整理
* オレンジクラウド（Cloudflareプロキシ）のオン・オフの動作差異を図解で整理
* DNSの名前解決フロー（ルートDNS → .com DNS → 権威DNS → キャッシュDNS → クライアント）を図解
* ネームサーバー移管手順の整理（お名前.com / さくら / Xサーバー対応表付き）
* サブパス方式（`example.com/blog`）とサブドメイン方式（`app.example.com`）の難易度比較
* Cloudflare WorkerによるURL pathベースのルーティングコード実装
* Next.jsの静的アセット（`/_next/static/...`）が404になる問題の原因特定と修正
* 「踏み台Pages」構成 → 「Worker直接カスタムドメイン紐づけ」構成への設計変更
* 設定手順書（Markdown）と全体構成図（PNG）の作成・更新

### 使用したツール・技術

* Cloudflare Workers（ルーティング・プロキシ）
* Cloudflare DNS（権威DNSサーバーとして）
* Vercel（静的サイトホスティング / Next.js）
* WordPress（さくら / Xサーバー等のレンタルサーバー）
* Python（matplotlib / IPAGothicフォント）構成図PNG生成

### 主要な意思決定とその理由

* **踏み台PagesをWorker直接紐づけに変更**：Cloudflare Workers の Settings → Domains & Routes → Custom Domain でカスタムドメインをWorkerに直接紐づけられることが判明。Pagesは不要で手順がシンプルになるため採用
* **サブパス方式を採用**：クライアント・受講生からの要件が「同一ドメイン（`example.com/blog`）でVercelを表示したい」であり、CNAMEを使うサブドメイン方式では要件を満たせないため
* **`/_next/`パスもWorkerでVercelに流す**：Next.jsの静的アセットが`example.com/_next/...`で取得されるため、Workerのルーティング条件に含める必要があった

---

## 3. 進捗と成果

### 達成できたこと

* `shogoworks.com/blog/` でVercelのコンテンツが表示されることを確認（別チャットで実動作確認済み）
* CSSが崩れる原因（`/_next/`パスがWorkerを素通りしていた）を特定・修正コード完成
* 設定手順書（Markdown）を教材レベルで整備完了（Step1〜6、トラブルシューティング、DNSチートシート付き）
* 全体構成図（日本語PNG）を生成・出力

### 定量的な成果

* 手順書：Step1〜6構成、約200行のMarkdown
* 構成図：1枚のPNG（Cloudflare内部構造・ルーティングロジック・設定ステップを一図に収録）
* Workerコード：約30行（`isVercelPath`関数 + fetch転送ロジック）

### 定性的な成果

* 「DNSはIPまでしか届けられない。パス振り分けはWorkerの仕事」という概念が明確に言語化できた
* 過去の失敗事例（AレコードをVercelに向けてWP全体が飛んだ）の原因が正確に説明できるようになった
* 踏み台Pages不要の設計は、Cloudflareを使ったプロキシ戦略の中でも最もシンプルな構成であり、クライアント提案・教材として転用しやすい

---

## 4. 学びとナレッジ

### うまくいったこと（Good）

* DNSの基礎概念（オレンジクラウド・ネームサーバー移管・権威DNS）をゼロから積み上げて整理できた
* 実動作確認（`shogoworks.com/blog/`での表示成功）がベースにあるため、手順書の信頼性が高い
* WorkerのCustom Domain直付けという最新UIの知識をクライアントから逆に教えてもらい、最新の正確な手順に更新できた

### うまくいかなかったこと（Bad）

* 初版の手順書に「踏み台Pages」が含まれており、実際の構成と乖離があった（クライアントフィードバックで修正）
* 構成図の日本語フォント問題（DejaVu Sansでは日本語非対応）で2回作り直しが発生。IPAGothicを明示的に指定することで解決

### 改善ポイント（Improve）

* 手順書の初版作成前に「踏み台Pagesは本当に必要か」を先に検証すべきだった
* 構成図生成はmatplotlibでフォントを明示的に指定する（`plt.rcParams['font.family'] = 'IPAGothic'`）をデフォルトにする

### 技術的な発見・Tips

* **DNSはパスを見ない**：`example.com/blog` と `example.com/` のどちらも、DNS解決の結果は同じIP。パス振り分けはLayer7（アプリケーション層）での処理が必要
* **WorkerにCustom Domainを直接紐づける方法**：Workers & Pages → 対象Worker → Settings → Domains & Routes → `+ Add` → Custom Domain。Pagesの踏み台不要
* **`/_next/`パスの扱い**：Next.js静的アセットは`/_next/static/...`から取得される。Workerで`/blog`だけでなく`/_next/`もVercelに流す条件が必要
* **MXレコードのネームサーバー移管リスク**：Cloudflareへのネームサーバー移管時、MXレコードが自動スキャンで取り込まれない場合があるため、移管前のスクリーンショット保管が重要
* **Custom DomainとRouteの違い**：Custom Domainはドメインまるごと紐づけ（シンプル）。Routeはパターンマッチング（`example.com/blog*`）で細かく制御可能

---

## 5. 課題と対応

### 発生した課題

* CSSが崩れる：`/_next/static/...`が`example.com`に向いて404
* 構成図が英語表記になっていた：日本語フォント未対応
* 手順書に踏み台Pagesの手順が含まれており実態と乖離

### 対応方法

* `isVercelPath`関数に`/_next/`と`/favicon`の条件を追加して再デプロイ
* `plt.rcParams['font.family'] = 'IPAGothic'`を明示してPNG再生成
* Step4を「Worker直接カスタムドメイン紐づけ」に差し替え、Pages関連の記述を全削除

### 未解決の課題

* Vercel側のNext.jsプロジェクトで`basePath: '/blog'`の設定が必要なケースがある（フレームワーク依存）
* 本番環境での動作確認（`shogoworks.com`以外のドメインでの汎用性検証）は未実施

---

## 6. コストとリソース

### 人的リソース

* 田中省伍：設計・検証・ドキュメント作成（1日）

### 金銭的コスト

* Cloudflare Freeプラン：$0
* Vercel Freeプラン：$0
* Workers：Freeプランで対応可（リクエスト数制限あるが個人用途は問題なし）

### コスト対効果

* 完了時に記入

---

## 7. 今後の展開

### 次のアクション

* Note記事として「Cloudflare Workerで同一ドメインにWP＋Vercelを共存させた話」を執筆・公開
* Bytech講座のインフラ系コンテンツへの組み込み検討
* `shogoworks.com/blog`でのVercel静的サイト本番稼働確認

### 横展開の可能性

* 同様の構成をクライアント案件（LP + 既存サービスの共存）に提案できる
* AI Workerを使ったより高度なルーティング（A/Bテスト・リージョン別振り分け）への発展余地あり
* DNS基礎〜Cloudflare設定の教材コンテンツとしてBytech講座に組み込む

### 長期的な改善案

* Workerコードのテンプレート化（WordPressサイト向け汎用プロキシテンプレート）
* Terraform/WranglerによるIaC化（SHO-137と連動）

---

📚 関連リソース

### 成果物・ドキュメント

* 設定手順書：`cloudflare-vercel-proxy-guide.md`（Step1〜6 + トラブルシューティング + DNSチートシート）
* 全体構成図：`cloudflare-vercel-architecture.png`（日本語、Cloudflare内部構造含む）
* Workerコード（本文に記載）

### 参考資料

* Cloudflare Workers ドキュメント：https://developers.cloudflare.com/workers/
* Cloudflare Workers Custom Domains：https://developers.cloudflare.com/workers/configuration/routing/custom-domains/
* 過去会話（Cloudflareドメイン移行）：https://claude.ai/chat/93e04e25-b445-447a-b8ce-7f85ba54b63d
* 過去会話（複数ホストでのドメイン運用）：https://claude.ai/chat/4af476f3-3ab3-4097-8835-416570888eae

### 関連プロジェクト

* SHO-137：IaC（Terraform × Claude Code）学習（インフラ自動化との連動）
* SHO-131：全PoCのai-verification-log整備・Notion転記

---

✅ メモ・雑記

* オレンジクラウドの「オン/オフ」がプロキシのオン/オフであることが、多くのエンジニアが混同しやすいポイント。「DNSはIPまでしか届けられない」という一言が一番スッキリ説明できる
* 「踏み台Pages」という表現は実態に近いが、正確には「ドメインの受け口」。Workerに直接Custom Domainを紐づける方法があるため現在は不要
* bytech.jpでも同様の構成（WordPressルート + Vercelのサブパス）を検討しているチャット履歴あり（別チャット: `4af476f3`）
* 構成図のPNG生成はmatplotlib + IPAGothicが安定。DejaVu Sansでは日本語が欠落する

---

## 📝 更新ログ
<!-- このセクションはスキルが自動で追記する。手動編集不要。 -->
| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/07 | ファイル作成（init）— 今日・昨日のチャット履歴をもとに全セクション記入 |
