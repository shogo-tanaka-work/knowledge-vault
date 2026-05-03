# Turnstile

## 一行サマリ
画像選択もチェックボックスもほぼ不要な、Cloudflareの次世代CAPTCHA代替。サイトをCloudflareにプロキシしていなくても利用できる独立サービスである。

## 解決する課題（Why）
従来のreCAPTCHAは「信号機を選べ」「横断歩道を選べ」といった操作でユーザー体験を著しく劣化させ、変換率を下げる。さらにGoogleによる行動追跡やCookie利用に対するプライバシー懸念が強く、GDPR/CCPA対応上のリスクにもなる。Turnstileはこれらを解決する。

- ユーザーの操作（画像選択など）を原則ゼロにする
- 個人を追跡するためのCookieやフィンガープリントを送信しない（Privacy Addendumに準拠）
- どのCDN・どのインフラ上でも動作する独立したCAPTCHA代替を提供する

## 主要機能（What）
- **3つのウィジェットモード**: Managed（推奨・自動判定）／ Non-interactive（操作不要だが表示あり）／ Invisible（完全非表示）
- **Siteverify API**: サーバー側でトークンを検証する公式エンドポイント
- **Pre-clearance**: SPAやサイト内遷移で、Cloudflare Challengeの「事前クリア」Cookieを発行しUXを向上させる
- **Turnstile Analytics**: 発行チャレンジ数・解決率・メトリクスを可視化
- **WCAG 2.2 AAA準拠**: アクセシビリティの最高水準を満たす
- **モバイル対応**: iOS / Android / WebView 向け実装ガイドあり
- **無料**: 利用量に上限なしで無償提供

## 動作の仕組み（簡易）
1. ブラウザに軽量JavaScriptウィジェットを埋め込む
2. ウィジェットが proof-of-work、proof-of-space、Web API調査、ブラウザの癖検出など複数の非対話チャレンジをバックグラウンド実行する
3. 信号を集めてリスクを評価し、必要時のみチェックボックス表示にフォールバックする
4. 成功時は最大2,048文字のトークンが発行される
5. サーバー側がそのトークンを `https://challenges.cloudflare.com/turnstile/v0/siteverify` に送信し、シークレットキーとともに正当性を検証する
6. トークンは300秒（5分）で失効、かつ一度しか検証できない

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- お問い合わせフォーム・ログイン・新規登録・コメント投稿・パスワードリセットなど、bot流入を防ぎたい入口全般
- reCAPTCHAからのリプレース（既存スクリプトの貼り替えで移行可能）
- プライバシー重視のサービス（GDPR領域、ヘルスケア、金融など）
- Cloudflareをプロキシ層に入れていないが、bot対策だけ欲しいケース（マルチクラウド・他社CDN利用環境）
- SPAでの体験を維持したまま保護したいケース（Pre-clearance活用）

### 適していないシーン
- 高度な敵対的bot（決済不正・スクレイピング業者）に対する単独防御。Bot Management・WAF・レート制限と組み合わせるべき
- ネイティブモバイルアプリ専用（WebViewが使えず、モバイル実装が許容できない場合）
- ブラウザ環境を持たないAPIクライアント間通信（mTLSやAPIキーを使うべき）
- ユーザー認証・認可そのもの（CAPTCHAは「人間判定」であって「本人判定」ではない）

## 競合・代替

| 観点 | Turnstile | reCAPTCHA v3 | hCaptcha |
|---|---|---|---|
| 提供元 | Cloudflare | Google | Intuition Machines |
| 操作要否 | 原則不要（Managedで必要時のみ） | 不要（スコア型） | 画像選択あり（Enterpriseで非表示化可） |
| プライバシー | Cookie/追跡なし、Privacy Addendum明示 | Google追跡あり、GDPR懸念強い | Google非依存、追跡少なめ |
| 料金 | 完全無料・無制限 | 無料枠あり、Enterprise有償 | 無料プランあり、Pro/Enterprise有償 |
| サーバー検証 | Siteverify API必須 | siteverify必須 | siteverify必須 |
| Cloudflare依存 | 不要（独立サービス） | 不要 | 不要 |
| アクセシビリティ | WCAG 2.2 AAA | 部分対応 | アクセシブル代替あり |

## 料金モデルの要点
- **完全無料**。利用回数・サイト数の上限なし
- 有償プランや「Turnstile Enterprise」のような分離は存在しない
- ビジネス価値: bot対策で年数十万円〜数百万円かかる他社CAPTCHAをゼロ円で置換可能

## 実装例（必須）

### 1. クライアント側（HTML埋め込み・implicit rendering）

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
</head>
<body>
  <form action="/login" method="POST">
    <input type="email" name="email" required />
    <input type="password" name="password" required />

    <!-- Turnstileウィジェット。dataのsitekeyは公開してよい -->
    <div class="cf-turnstile"
         data-sitekey="0x4AAAAAAAxxxxxxxxxxxxx"
         data-theme="auto"
         data-size="normal"></div>

    <button type="submit">ログイン</button>
  </form>
</body>
</html>
```

フォーム送信時、`cf-turnstile-response` という名前で自動的にトークンが付与される。

### 2. サーバー側（Node.js / Hono などでの検証）

```ts
// POST /login のハンドラ
app.post('/login', async (c) => {
  const body = await c.req.parseBody();
  const token = body['cf-turnstile-response'];
  const ip = c.req.header('CF-Connecting-IP') ?? '';

  const form = new FormData();
  form.append('secret', process.env.TURNSTILE_SECRET_KEY!); // サーバー側のみ保持
  form.append('response', String(token));
  if (ip) form.append('remoteip', ip);

  const res = await fetch(
    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
    { method: 'POST', body: form }
  );
  const outcome = (await res.json()) as { success: boolean; 'error-codes'?: string[] };

  if (!outcome.success) {
    return c.text(`Turnstile verification failed: ${outcome['error-codes']?.join(',')}`, 403);
  }

  // ここから本来の認証処理
  return c.text('OK');
});
```

### 3. テストキー
本番デプロイ前に、Cloudflare公式のテスト用sitekey/secret keyを使えば、実チャレンジを発火させずに統合テストができる。

## 制限・注意点
- **サーバー検証は必須**。クライアント側で完結させると無意味であり、Turnstile Analyticsの検証メトリクスがゼロのままになる
- **トークンの有効期限は300秒、再利用不可**。長時間入力フォームでは再発行（リフレッシュ）の仕組みを用意する
- **`challenges.cloudflare.com` への接続が必要**。CSPで `script-src` `frame-src` `connect-src` を許可する
- **シークレットキーをクライアントに露出させない**。GitやフロントエンドJSへの混入は事故の典型例
- **Invisibleモード使用時はプライバシーポリシーへの記載義務**がある（Cloudflare Turnstile Privacy Addendumへの参照）
- **CAPTCHAは万能ではない**。WAF・Bot Management・レート制限と多層防御で組み合わせる
- **古いブラウザは非対応**。エラー状態（Outdated or unsupported browser）が表示される

## 参考リンク
- [Turnstile Overview (Cloudflare Docs)](https://developers.cloudflare.com/turnstile/)
- [Get started](https://developers.cloudflare.com/turnstile/get-started/)
- [Turnstile widgets (Concepts)](https://developers.cloudflare.com/turnstile/concepts/widget/)
- [Turnstile Privacy Addendum](https://www.cloudflare.com/application-services/products/turnstile-privacy/)

---
参照日: 2026-05-03
