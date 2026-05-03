# Cloudflare Tunnel

## 一行サマリ
cloudflared デーモンがオリジンからCloudflareエッジへアウトバウンド接続のみを張り、公開IP・インバウンド開放なしで内部サービスを安全に公開・接続する仕組みである。

## 解決する課題（Why）
- オリジンサーバーに公開IPアドレスを割り当てたくない、または割り当てられない（NAT越え、CGNAT配下、家庭・社内環境）。
- ファイアウォールでインバウンドポート（80/443等）を開けたくない。開けるとDDoSや脆弱性スキャンの対象になる。
- 従来型VPN（IPSec/OpenVPN）の運用負荷（証明書配布、クライアント設定、固定IP）から脱却したい。
- 開発環境やオンプレシステムを、特定メンバー・SaaS・クラウドから安全に到達可能にしたい。
- Cloudflare WAF/Bot Management/Access の前段保護を、オリジンを露出させずに適用したい。

## 主要機能（What）
- **cloudflared デーモン**: オリジン側で動作する軽量Goバイナリ。常駐してCloudflareエッジへ持続的トンネルを確立。
- **Public Hostname**: トンネルに紐づく公開ホスト名（example.com）からオリジンへルーティング。HTTP/HTTPS/SSH/RDP等に対応。
- **Private Network ルーティング**: CIDR単位で内部ネットワーク全体をCloudflare WARP クライアント経由で到達可能に（VPN代替）。
- **Connector レプリカ**: 同一トンネルに複数 cloudflared プロセスを並列起動し、HA・無停止デプロイ・負荷分散を実現。
- **TLS 1.3 + 耐量子暗号**: トンネル経路はデフォルトで暗号化、将来の量子計算機脅威にも対応。
- **リモート管理（dashboard管理）/ ローカル設定ファイル管理（config.yml）** の2方式を選択可。

## 仕組み（必須セクション）
1. オリジン側ホスト（VM/コンテナ/RasPi等）に `cloudflared` をインストール。
2. `cloudflared tunnel login` でCloudflareアカウントを認証し、トンネル（UUID識別）を作成する。
3. 起動した cloudflared はCloudflareエッジ（最寄りデータセンター）へ **outbound HTTPS/QUIC** で接続を張りっぱなしにする。複数Connector接続が冗長化される。
4. ユーザーが公開ホスト名にアクセスすると、CFエッジは該当トンネルにリクエストを多重化転送し、cloudflared がオリジン上のローカルサービス（例: `http://localhost:3000`）へプロキシする。
5. ファイアウォールはアウトバウンドのみ許可すればよく、インバウンドは完全クローズドのままにできる（Zero Trust の前提条件）。

```
[Origin] → cloudflared --(outbound TLS)--> [CF Edge] ← User
              ↑                              ↑
       インバウンド完全閉鎖              WAF/Access/Bot
```

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 社内ツール（Backstage、Grafana、Wiki等）を社外から安全に公開したい。
- オンプレ・自宅サーバーをHTTPSで公開したい（ngrokの本番代替）。
- 開発環境を顧客やチームメンバーに一時共有したい。
- Kubernetesクラスタ内サービスを公開IP・LoadBalancerなしで公開したい。
- VPNを廃止しゼロトラスト（ZTNA）へ移行したい。社員のデバイスから内部ネットワークへ。
- ハイブリッドクラウド構成でオンプレ↔クラウド間を専用線なしで繋ぎたい。

### 適していないシーン
- Cloudflare以外のCDN/WAFを前段に置きたい場合（経路がCFに固定される）。
- 超低レイテンシ・極端な高スループットが要求される（金融取引等）。トンネル経由の追加ホップ分のオーバーヘッドあり。
- 完全オフライン環境（cloudflared がCFエッジへ常時接続必須）。
- UDP固有プロトコル（一部対応するが要設計確認）。

## 競合・代替

| 観点 | Cloudflare Tunnel | ngrok | Tailscale | Twingate | AWS Site-to-Site VPN |
|---|---|---|---|---|---|
| モデル | Outbound Tunnel + ZTNA | Outbound Tunnel | WireGuard P2P Mesh | ZTNA Connector | IPSec VPN |
| 公開IP不要 | はい | はい | はい | はい | いいえ（VGW必要） |
| 無料枠 | 基本無料・無制限 | 制限あり（同時接続/帯域） | 個人/小規模無料 | 無料プランあり | なし（時間課金） |
| 認証統合 | Cloudflare Access（IdP連携） | 限定的 | OIDC連携 | IdP統合強い | IAM/別途 |
| 公開URL | カスタムドメイン標準 | ランダムまたは有料カスタム | プライベートのみ | プライベートのみ | プライベートのみ |
| WAF/DDoS | CF全機能適用 | 一部 | なし | なし | なし |
| ベンダーロック | Cloudflare依存 | ngrok依存 | 比較的軽 | Twingate依存 | AWS依存 |

ngrok は開発用途、Tailscale は社員間Mesh、Tunnel は「公開＋ZTNA」を一気通貫で提供する点で差別化される。

## Access との組合せ（必須セクション）
Cloudflare Tunnel 単体では、公開ホスト名を知っていれば誰でもアクセスできてしまう。これを認証ゲートで保護するのが **Cloudflare Access** である。

- Tunnel = 「内部サービスをCFエッジに繋げる輸送層」
- Access = 「CFエッジでIdP認証・ポリシー判定を行う認可層」

組み合わせパターン（典型ZTNA構成）:
1. オリジンに cloudflared を配置し Tunnel を確立（インバウンド遮断）。
2. 公開ホスト名 `internal-tool.example.com` をトンネルに紐づける。
3. Access Application を同ホスト名に設定し、Google Workspace / Okta / Azure AD などのIdPを連携。
4. ポリシー例: 「`@example.com` ドメインかつ社用デバイスのみ許可」。
5. ユーザーは ブラウザでSSO → Access JWT発行 → Tunnel経由でオリジン到達。VPNクライアント不要。

これによりVPN置換・SaaS的アクセス体験・きめ細かな条件付きアクセス（デバイス姿勢、地理、時間帯）を実現できる。SSH/RDPもブラウザレンダリングで提供可能（Browser Rendering連携）。

## 料金モデルの要点
- **cloudflared / Tunnel 自体は無料**。トンネル本数・帯域・データ転送量に追加料金なし。
- **Cloudflare Zero Trust（Access含む）**: 50ユーザーまで無料、超過分は$7/user/月（Standardプラン、2026年時点目安）。
- **Private Network（WARP経由内部ネット到達）** もZero Trustライセンス枠内。
- 課金されるのは「ユーザー数（Access利用時）」と「上位機能（Browser Isolation、Gateway DLP等）」であり、トンネル基盤は実質無料で利用できる。

## CLI / IaC 操作例

### cloudflared CLI（ローカル管理トンネル）
```bash
# インストール（macOS）
brew install cloudflared

# 認証（ブラウザでCFアカウントを選択）
cloudflared tunnel login

# トンネル作成（UUIDが発行される）
cloudflared tunnel create my-tunnel

# DNSレコードを公開ホスト名にバインド
cloudflared tunnel route dns my-tunnel app.example.com

# 設定ファイル（~/.cloudflared/config.yml）
# tunnel: <UUID>
# credentials-file: /root/.cloudflared/<UUID>.json
# ingress:
#   - hostname: app.example.com
#     service: http://localhost:3000
#   - service: http_status:404

# 起動（フォアグラウンド検証）
cloudflared tunnel run my-tunnel

# サービス化（systemd登録）
sudo cloudflared service install
```

### リモート管理トンネル（Dashboard / API / Terraform）
- ダッシュボードで作成 → 発行された Tunnel Token を使い `cloudflared tunnel run --token <TOKEN>` だけで起動。
- 設定（ingress, public hostname）はダッシュボードから編集、即時反映。
- Terraform `cloudflare_tunnel` / `cloudflare_tunnel_config` リソースでIaC化可能。

## 制限・注意点
- cloudflared は常にCFエッジへ接続できる必要がある。完全閉域網では使えない。
- 経路がCloudflareネットワークに固定される（マルチCDN戦略との両立は要設計）。
- 1トンネルあたりのConnector数・同時接続数にアカウント制限あり（Account limits参照）。
- 大量のWebSocket/長時間接続は接続上限・タイムアウト挙動に注意。
- cloudflared プロセスの権限管理（非rootで動かす、トークン漏洩対策）が必須。トークンはトンネル全権限を持つ。
- ログ・メトリクスはデフォルトで控えめ。本番運用ではログレベル・メトリクスエンドポイント設定を行い、ヘルスアラートを構成する。
- 設定変更（ingress追加等）はリモート管理なら即時、ローカル管理なら cloudflared 再起動が必要。

## 参考リンク
- 公式: <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/>
- Get started: <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/>
- Configure a tunnel: <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/configure-tunnels/>
- Reference architecture: Cloudflare One Reference Architecture（公式ドキュメント内）
- 関連スキル: Cloudflare Access（ZTNA）、Cloudflare WARP（クライアント）

---
参照日: 2026-05-03
