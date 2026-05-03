# Cloudflare CLI / IaC ツール ガイド

Cloudflareリソースをコードで操る方法は4系統ある。役割が違うので混同しない。

## 4つのツール

### 1. Wrangler — Workers 中心の公式CLI

Workers / Pages / R2 / D1 / KV / Queues などDeveloper Platform のローカル開発・デプロイのデファクト。`wrangler dev` でローカルエミュレーションができ、`wrangler deploy` で本番反映。設定は `wrangler.jsonc` (or `.toml`) に集約する。

```bash
wrangler init my-worker
wrangler dev          # ローカル実行
wrangler deploy       # 本番デプロイ
wrangler r2 bucket create my-bucket
wrangler d1 execute mydb --command "SELECT 1"
```

### 2. cf CLI — 全プロダクト対応の次世代CLI（技術プレビュー）

2026年に発表された新CLI。最終的に Cloudflare API ほぼ3,000操作を統一インタフェースで提供する予定。現状は一部製品のみ。Wranglerと将来統合される計画。

特徴:
- `--local` でローカル/リモート切替
- `--json` 全コマンド対応
- 命名統一 (`get` のみ・`info` 廃止、`--force` のみ・`--skip-confirmations` 廃止)

```bash
cf workers list --json
cf r2 bucket get my-bucket --local
```

参考: [Try the cf CLI Local Explorer](https://blog.cloudflare.com/cf-cli-local-explorer/)

### 3. Terraform — インフラ全体のIaC定番

Cloudflare の Terraform Provider はDNS、WAFルール、ゾーン設定、Access ポリシー、Workers route など **管理系設定** をコード化する用途に強い。アプリのコードデプロイは Wrangler、ガバナンス系は Terraform、と分担するのが現実解。

```hcl
resource "cloudflare_record" "www" {
  zone_id = var.zone_id
  name    = "www"
  type    = "A"
  content = "192.0.2.1"
}
```

### 4. Pulumi — 言語SDKでIaC

TypeScript / Python / Go などで Cloudflare リソースを記述したい場合の選択肢。Terraform の用途と被るが、既存コードベースの言語に揃えたい場合に。

## 使い分け早見表

| やりたいこと | 推奨ツール |
|------------|----------|
| Worker のローカル開発 / デプロイ | **Wrangler** |
| R2 / D1 / KV / Queues の操作 | **Wrangler** |
| DNS レコード / WAF / Access ポリシーの管理 | **Terraform** |
| 一回限りの調査・スクリプト | **cf CLI** または `curl` でAPI |
| アプリ言語と揃えてIaC | **Pulumi** |
| GUI で十分 | Cloudflare Dashboard |

## CI/CD パターン

```
GitHub → GitHub Actions:
  ├─ wrangler deploy           # アプリコード
  └─ terraform apply           # ゾーン設定・WAF・Access ポリシー
```

シークレット管理は `wrangler secret put` または GitHub Secrets → Actions。

## ハマりどころ

- **Wrangler のバージョン差**: v3 と v4 で `wrangler.toml` フォーマットが微妙に変わる。新規は `wrangler.jsonc` 推奨
- **Terraform Provider のメジャー更新破壊的変更**: 4.x → 5.x で Ruleset 系API がリソース分割された。アップグレード前に CHANGELOG 必読
- **Account ID と Zone ID の混同**: ほぼ全コマンドで必須。`.env` か CI Secrets に固定しておく
- **ローカル開発の挙動とprod差**: Workers の `nodejs_compat` フラグ、Durable Objects のトランザクション、Cron Triggers の発火タイミングは要注意

## 参考リンク

- [Wrangler Docs](https://developers.cloudflare.com/workers/wrangler/)
- [Cloudflare Terraform Provider](https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs)
- [Cloudflare API Reference](https://developers.cloudflare.com/api/)

---
参照日: 2026-05-03
