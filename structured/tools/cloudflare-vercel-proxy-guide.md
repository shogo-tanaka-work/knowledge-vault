# Cloudflare × Vercel サブパスプロキシ 設定手順書

> **目的：** `example.com` で動くWordPressはそのままに、`example.com/blog` だけVercelの静的サイトを表示させる

---

## 全体の構成イメージ

```
ユーザー
  ↓（DNS解決 → CloudflareのIPが返る）
Cloudflare Worker（example.com に直接紐づけ）
  ├── /blog, /blog/*, /_next/* → Vercel（静的サイト）
  └── それ以外                 → WordPressサーバー（さくら / Xサーバー等）
```

**ポイント：**
- WorkerにはカスタムドメインをSettings → Domains & Routes から直接紐づけられる（踏み台のPages不要）
- パスで振り分けるのはCloudflare Workerの仕事。DNSはIPまでしか届けられない

---

## Step 1｜Cloudflareアカウント作成・ドメイン追加

### 1-1. アカウント作成

1. [https://cloudflare.com](https://cloudflare.com) にアクセス
2. 「Sign Up」からメールアドレスとパスワードで登録
3. プランは **Free** を選択

### 1-2. ドメインを追加

1. ダッシュボード → **「Add a Site」**
2. ドメイン名を入力（例：`example.com`）
3. プランは **Free** のまま続行
4. CloudflareがDNSレコードを自動スキャンして取り込む

> **確認ポイント：** 自動スキャンで既存のレコードが引き継がれているか確認する（次Stepで詳細確認）

---

## Step 2｜ネームサーバー変更（DNS管理をCloudflareに移管）

### 2-1. Cloudflareが指定するネームサーバーを確認

自動スキャン後の画面に2つのネームサーバーが表示される。

```
xxx.ns.cloudflare.com
yyy.ns.cloudflare.com
```

この値をメモしておく。

### 2-2. ドメイン取得サービス側でネームサーバーを変更

| サービス | 設定場所の目安 |
|---|---|
| お名前.com | ドメイン設定 → ネームサーバーの変更 |
| さくらインターネット | ドメインメニュー → ネームサーバー設定 |
| Xサーバー | サーバーパネル → ドメイン設定 |

先ほどメモした2つのネームサーバーを入力して保存。

> **注意：** 反映まで最大48時間かかる。Cloudflareのダッシュボードに「有効化されました」と表示されれば完了。

---

## Step 3｜DNSレコードの確認と整備

ネームサーバーの変更が完了したら、Cloudflareの **DNS管理画面** でレコードを確認する。

### 確認すべきレコード一覧

| レコード種別 | 名前 | 値 | オレンジクラウド | 用途 |
|---|---|---|---|---|
| A | `@`（ルートドメイン） | WordPressサーバーのIP | オン | WPへの通信 |
| A | `www` | WordPressサーバーのIP | オン | wwwアクセス |
| MX | `@` | メールサーバー | **オフ** | メール配送 |
| TXT | `@` | SPF / サーチコンソール等 | — | 各種認証 |

### よくある確認ポイント

- **MXレコード：** 自動スキャンで取り込まれているか必ず確認。消えていると**メールが届かなくなる**
- **TXTレコード：** Googleサーチコンソール認証やSPFが設定されていた場合、引き継がれているか確認
- **移管前にスクリーンショットを撮っておくと安全**

### WordPressサーバーのIPアドレスの調べ方

さくら・Xサーバー等のサーバー管理画面 → **「サーバー情報」または「IPアドレス」** の項目に記載されている。

---

## Step 4｜Cloudflare Worker を作成してカスタムドメインを直接紐づける

### 4-1. Workerを新規作成

1. Cloudflareダッシュボード → **Workers & Pages**
2. **「Create」** → **「Create Worker」**
3. 名前をつける（例：`blog-proxy`）
4. デフォルトのコードのまま一旦 **「Deploy」**

### 4-2. カスタムドメインを直接紐づける

1. 作成したWorkerを開く → **「Settings」タブ**
2. **「Domains & Routes」** セクションの **「+ Add」** をクリック
3. モーダルで **「Custom Domain」** を選択
   - RouteとCustom Domainの2択が出る場合は **Custom Domain** を選ぶこと
4. `example.com` を入力して追加

> **Custom Domain と Route の違い：**
> - **Custom Domain**：ドメインまるごとWorkerに紐づける。シンプルで今回の用途に適している
> - **Route**：`example.com/blog*` のようにパターンで細かく制御できる。今回はWorker内でパス判定するためCustom Domainで十分

追加後、CloudflareのDNS管理画面にWorker向けのレコードが自動追加されているか確認する。

---

## Step 5｜Workerにルーティングコードを書く

Workerの **「Edit Code」** を開いて以下のコードを貼り付ける。

```javascript
const BLOG_ORIGIN = 'https://your-app.vercel.app'; // ← VercelのURLに変更

function isVercelPath(path) {
  return path === '/blog'
    || path.startsWith('/blog/')
    || path.startsWith('/_next/')   // Next.jsのCSS・JS
    || path.startsWith('/favicon'); // ファビコン
}

export default {
  async fetch(request) {
    const url  = new URL(request.url);
    const path = url.pathname;

    if (isVercelPath(path)) {
      // /blog プレフィックスを除いてVercelに渡す
      const stripped = path.startsWith('/blog')
        ? (path.replace(/^\/blog/, '') || '/')
        : path;

      const target = new Request(
        BLOG_ORIGIN + stripped + url.search,
        request
      );
      target.headers.set('Host', 'your-app.vercel.app'); // ← Vercelのホスト名
      target.headers.set('X-Forwarded-Host', 'example.com'); // ← 自分のドメイン
      return fetch(target);
    }

    // /blog 以外はWordPressへ通常通り転送
    return fetch(request);
  }
};
```

> **変更箇所は3か所：**
> 1. `BLOG_ORIGIN` にVercelのデプロイURL
> 2. `Host` ヘッダーにVercelのホスト名
> 3. `X-Forwarded-Host` に自分のドメイン

「Deploy」して完了。

---

## Step 6｜動作確認

| URL | 期待する結果 |
|---|---|
| `example.com/` | WordPressのトップページが表示される |
| `example.com/blog` | Vercelの静的サイトが表示される |
| `example.com/blog/post-1` | Vercelのページが表示される |

### CSSが崩れる場合

Next.jsの静的アセット（`/_next/static/...`）が `example.com` に向いてしまい404になっているケース。  
`isVercelPath` 関数に `/_next/` の条件が入っているか確認して再デプロイする。

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| WordPressも含め全部Vercelに飛ぶ | AレコードをVercelのIPに向けてしまった | AレコードをWordPressサーバーのIPに戻す |
| `/blog` が404になる | WorkerコードのパスマッチかCustom Domain未設定 | `isVercelPath` の条件とSettings → Domains & Routesを確認 |
| CSSが崩れる | `/_next/` パスがVercelに流れていない | `isVercelPath` の条件を確認・再デプロイ |
| メールが届かなくなった | MXレコードが移管時に消えた | Cloudflare DNSにMXレコードを再追加 |
| 反映されない | DNSのキャッシュ | 最大48時間待つ / ブラウザキャッシュをクリア |

---

## DNS レコード用語チートシート

| レコード | 役割 | 今回の用途 |
|---|---|---|
| **A** | ドメイン → IPv4アドレス | WordPressサーバーのIPを紐づける |
| **AAAA** | ドメイン → IPv6アドレス | IPv6対応時に使用（なければ不要） |
| **CNAME** | ドメイン → 別のドメイン名 | サブドメインをVercelに向ける場合に使う（今回は不使用） |
| **MX** | メール配送先サーバーの指定 | NS移管後に消えていないか必ず確認 |
| **TXT** | 任意テキスト情報 | SPF・DKIM・サーチコンソール認証など |
| **NS** | 権威DNSサーバーの指定 | Cloudflareに移管するときレジストラ側で変更 |

---

## 設定完了後の構成

```
example.com/          → Cloudflare Worker → WordPressサーバー（さくら/Xサーバー等）
example.com/blog      → Cloudflare Worker → Vercel静的サイト
example.com/blog/*    → Cloudflare Worker → Vercel静的サイト
example.com/_next/*   → Cloudflare Worker → Vercel（アセット）
```

WordPressもVercelも既存の設定は一切変更不要。  
Cloudflare Workerだけで振り分けが完結する。踏み台としてのPagesは不要。
