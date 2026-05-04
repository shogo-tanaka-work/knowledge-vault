# Realtime (SFU / TURN / RealtimeKit)

## 一行サマリ
Cloudflare Realtimeは、WebRTCの3層インフラ（メディア中継のRealtime SFU、NAT/FW越えのRealtime TURN、プリビルドUI付きSDKのRealtimeKit＝旧Dyte）をAnycast網の上に統合提供し、ビデオ会議・ライブ配信・ゲーム音声・IoT遠隔監視のリアルタイム通信を、自前のSFU運用やリージョン分散の苦労なしに数百都市規模で展開できる「Real-time Serverless」プラットフォームである。

## 解決する課題（Why）
WebRTCをプロダクション運用する場合、SFU（Selective Forwarding Unit）の自前構築・リージョン分散・TURN中継・NAT越え失敗率・録画ストレージ・話者文字起こしまで、垂直に積み上げる必要がある。EC2にmediasoupやpionを立てるところまでは1人で書けるが、シンガポール・東京・フランクフルトに分散配置し、最寄りエッジに引き寄せ、参加者100人を越えても落ちないようにする時点で専任のWebRTCエンジニアが必要になる。Cloudflare Realtimeはこの状況を以下のように解決する。

- Realtime SFUがCloudflareの数百都市にデプロイ済みのAnycast SFUとして動き、参加者は最寄りエッジに自動接続される（リージョン選択コードゼロ）。
- Realtime TURNがturn.cloudflare.comというAnycast単一エンドポイントで、企業ファイアウォール越えのリレーをグローバル提供する（追加インフラ不要）。
- RealtimeKit（旧Dyte買収）が、ビデオ会議UIコンポーネント・録画・文字起こし・ブレイクアウトルームをSDK1行レベルで提供し、Zoom/Whereby代替のアプリを最短で立ち上げられる。
- Workers / Durable Objects と組み合わせて、入退室イベント・モデレーション・ライブ翻訳をエッジで処理できる（メディアパスとシグナリング/制御パスが同じCloudflareネットワーク内に閉じる）。
- SFU出力1,000GB/月までの無料枠＋$0.05/GBという、AgoraやTwilio Videoの分課金より圧倒的に予測しやすい料金体系を提供する。

## 主要機能（What）

### Realtime SFU
WebRTCメディアサーバーの中核。クライアントがCloudflareのAnycast IPに対してWebRTC PeerConnectionを張り、`session` → `tracks`（push/pull）→ `datachannels`という3階層のREST APIで操作する。

- **Session**：1クライアント1セッション。`POST /apps/{app_id}/sessions/new` でセッションIDを発行し、SDP offer/answerを交換する。
- **Tracks**：そのセッションに対して「Pushする（送信）」「Pullする（他セッションのトラックを購読）」を個別に登録する。SimulcastとSVC（Scalable Video Coding）に対応し、購読者ごとに異なる解像度・ビットレートを選択的に転送する（=SFUの本質）。
- **DataChannels**：WebRTCの任意データチャネルもSFU経由でファンアウトでき、ゲーム同期・チャット・カーソル共有等のリアルタイムデータを「メディアと同じ経路」で扱える。
- **WebRTC CDN モード**：1対多配信に最適化したモードで、ライブ配信（数千〜数万視聴者）を低レイテンシで配信する。SFU/CDNハイブリッド構成も可能。

### Realtime TURN
WebRTCのNAT/FW越えリレー。`turn.cloudflare.com`という単一ホスト名がAnycastで解決され、世界中どこからでも最寄りCloudflareエッジに着地する。

- 対応プロトコル：STUN/TURN over UDP（3478, 代替53）、TURN over TCP（3478, 代替80）、TURN over TLS（5349, 代替443）。443/TLSのおかげで、企業ファイアウォール下でも貫通できる。
- 短期credentialをAPI経由で発行（HMAC方式）。ICE serverに渡すだけで標準WebRTCライブラリが自動的に利用する。
- Realtime SFUと組み合わせて使う場合、TURN利用分は無料（SFU側の帯域課金に統合される）。
- 単独利用（自前SFU・他社SFUとの組み合わせ）の場合は$0.05/GBの帯域課金。

### RealtimeKit（旧Dyte）
2024年買収のDyteをCloudflareブランドに統合した、ビデオ会議向けプリビルドSDK。

- **UI Kit**：React / Vue / Angular / Web Components / iOS / Android / React Native / Flutter向けのコンポーネントライブラリ。`<DyteMeeting />`相当の1コンポーネント貼るだけで会議UIが立ち上がる。
- **Core SDK**：UIなしでメディア・参加者・録画を制御するためのクライアントSDK。独自UIを組む場合のレイヤ。
- **REST API**：ミーティング作成、参加者管理、録画・録画ファイルダウンロード、Webhook配信。
- **付帯機能**：録画（クラウド録画→ストレージ保存）、ライブ文字起こし、ブレイクアウトルーム、投票、バーチャル背景、チャット。Zoom/Whereby代替として必要なものが揃う。
- バックエンドはRealtime SFUの上に乗っており、SFUの恩恵（Anycast・分散）をそのまま受ける。

### Recording / Transcription
クラウド録画はRealtimeKit側で標準提供。録画ファイルはR2など任意のストレージに払い出し可能で、後段でWorkers AIによるサマライズ・Workers AI Whisperでの文字起こし再処理にもつなげられる。ライブ文字起こしはミーティング中にリアルタイム配信される。

### Workers / Durable Objects 連携
シグナリング・認可・モデレーションをWorkersで実装し、Durable Objectsで部屋単位の状態（参加者リスト・発言権・モデレーション状態）を保持するパターンが標準。SFUのメディアと制御プレーンが同じCloudflare網に閉じるため、レイテンシも経路コストも最小化される。Orange Meetsという公式デモアプリ（GitHub）がこの構成の参考実装になっている。

### Anycast / グローバル分散
全機能がCloudflareの300+都市Anycast網の上に乗る。利用者は「リージョンを選ぶ」概念がなく、最寄りエッジが自動的に応答する。中国本土からの接続のみ別扱い（Anycast対象外）である点に注意。

## アーキテクト視点：いつ選ぶか

### 適しているシーン
- 自前のビデオ会議・ウェビナー・教育プロダクトをゼロから作るケース。RealtimeKitで2週間でMVPを立ち上げ、必要に応じてSFU直叩きにレイヤダウンできる。
- 既存アプリにビデオ通話・音声通話を「機能の一部として」埋め込みたいSaaS（顧客サポート、医療相談、家庭教師マッチング等）。SDK埋め込みで完結する。
- マルチパーティのライブ配信（数百〜数万視聴者の低レイテンシ配信）。WebRTC CDNモードで構築する。
- ゲーム音声チャット・チームボイス。SFUのDataChannelでゲーム状態同期、メディアトラックで音声を流すワンストップ構成が可能。
- IoT・遠隔監視のRTSPに代わる現代的なリアルタイム映像配送（カメラ→SFU→ダッシュボード）。
- 既にCloudflareにWorkers / R2 / D1 / Durable Objectsで投資済みで、「制御プレーンとメディアを同一ベンダに寄せたい」組織。

### 適していないシーン
- 既にAgora / Twilio Video / 100ms / LiveKit / Vonage Videoに大規模投資済みで、SDK・録画・分析の運用フローが固まっているケース。乗り換えコストに見合わない。
- 中国本土ユーザー比率が高いプロダクト。CloudflareのAnycastは中国本土を含まないため、AgoraやTencent RTCの方が筋が良い。
- 1対1のシンプルなP2P通話で、TURN中継すらほぼ不要なケース。素のWebRTC + 公開STUNサーバーで足りる。
- E2EE（End-to-End Encryption）が法令・契約上の絶対要件で、SFUがメディアを復号できる構成が許されないケース。SFUは原理的にメディアを中継するため、Insertable Streamsベースの追加実装が必要になる。
- レイテンシ要件が極限（<50ms global）で、WebRTC+SFUの中継で発生する数十msすら許容できない超低遅延ゲーム配信。専用UDPプロトコル＋ピア直結が必要になる。
- オンプレ完結要件（医療・防衛・金融の一部）。Cloudflare上のマネージドSFUを通せない以上、選択肢に入らない。

## 競合・代替

| 観点 | Cloudflare Realtime | Agora.io | Twilio Video | 100ms | Daily.co | LiveKit | Amazon IVS Real-Time | Vonage Video |
|---|---|---|---|---|---|---|---|---|
| SFU提供形態 | Anycast SFU + TURN | リージョナルSD-RTN | リージョナルSFU（2024 EOL予定→Programmable Video縮小） | リージョナルSFU | リージョナルSFU | OSS（自前ホスト）+ Cloud | AWSリージョナル | リージョナルSFU |
| プリビルドUI SDK | RealtimeKit（旧Dyte） | 公式UI Kit | 限定 | Prebuilt SDK | Daily Prebuilt | Components | UI Kit | Video API SDK |
| 録画 / 文字起こし | RealtimeKitに統合 | 別途課金 | 別途課金 | 標準提供 | 標準提供 | 別途追加 | 別途S3保存 | 別途課金 |
| グローバル展開 | 300+都市 Anycast | 200+データセンター | AWS依存 | 主要リージョン | 主要リージョン | 自前次第/Cloud | AWSリージョン | リージョナル |
| 中国本土 | 非対応 | 強い | 限定 | 限定 | 限定 | 自前次第 | 限定 | 限定 |
| 料金モデル | SFU $0.05/GB（1TB無料）+ RealtimeKit分課金 | 分課金（参加者×分） | 分課金 | 分課金 | 分課金 | OSSは自前帯域、Cloud分課金 | 分+帯域 | 分課金 |
| Workers/エッジ統合 | 同一ネットワーク内で完結 | 別ベンダ連携 | 別ベンダ連携 | 別ベンダ連携 | 別ベンダ連携 | 自前 | AWS Lambda連携 | 別ベンダ連携 |
| OSS自前ホスト | 不可（マネージド） | 不可 | 不可 | 不可 | 不可 | 可（Apache 2.0） | 不可 | 不可 |

Cloudflare Realtimeの差別化は「Anycast SFU」「Workers/R2/Durable Objectsとのゼロ距離統合」「帯域ベースの単純料金」の3点。一方、分課金で参加者数を確実にコスト予測したいエンタープライズや、中国対応必須のプロダクトはAgoraに分がある。LiveKitは自前ホスト要件があるなら最有力代替。

## 料金

- **Realtime SFU**：月1,000GB（=1TB）の出力まで無料。それ以降は$0.05/GB（Cloudflareエッジから視聴者方向への帯域）。受信は無課金。
- **Realtime TURN**：Realtime SFUと併用時は無料。単独利用（自前SFU・サードパーティSFU経由）の場合は$0.05/GB（CloudflareエッジからTURNクライアント方向）。
- **RealtimeKit**：参加者×分単位の課金（具体単価はRealtimeKitダッシュボードで個別確認）。録画・文字起こしは追加課金枠。
- **Workers / R2 / Durable Objects**：シグナリング・録画ストレージとして使う場合は各サービスの通常料金が別途加算される（例：R2は$0.015/GB-月、エグレス無料）。

WebRTCの一般的な大原則として「動画を流す方向＝下り＝視聴者側」で帯域が伸びるので、グループ会議よりライブ配信型の方が課金が膨らみやすい。Simulcast/SVCで購読者の解像度を下げる設計が直接コスト削減になる。

## CLI / API 例

### TURN credentials 発行（curl）
```bash
# RealtimeアプリのTURN keyを使い、短期TURN credentialを発行
curl -X POST "https://rtc.live.cloudflare.com/v1/turn/keys/$TURN_KEY_ID/credentials/generate-ice-servers" \
  -H "Authorization: Bearer $TURN_KEY_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{ "ttl": 86400 }'
# → { "iceServers": { "urls": [...], "username": "...", "credential": "..." } }
```

クライアント側ではこれをそのままRTCPeerConnectionのiceServersに渡す。

```js
const pc = new RTCPeerConnection({
  iceServers: [
    {
      urls: [
        "stun:stun.cloudflare.com:3478",
        "turn:turn.cloudflare.com:3478?transport=udp",
        "turns:turn.cloudflare.com:5349?transport=tcp",
      ],
      username: TURN_USER,
      credential: TURN_CRED,
    },
  ],
});
```

### Realtime SFU セッション作成 → トラック push
```bash
# 1) 新規セッション作成
curl -X POST "https://rtc.live.cloudflare.com/v1/apps/$APP_ID/sessions/new" \
  -H "Authorization: Bearer $APP_TOKEN" \
  -H "Content-Type: application/json" \
  --data "{\"sessionDescription\": {\"type\":\"offer\",\"sdp\":\"<LOCAL_SDP_OFFER>\"}}"
# → { "sessionId": "abc123", "sessionDescription": {"type":"answer","sdp":"..."} }

# 2) このセッションでローカルトラックをpush（送信）
curl -X POST "https://rtc.live.cloudflare.com/v1/apps/$APP_ID/sessions/abc123/tracks/new" \
  -H "Authorization: Bearer $APP_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "sessionDescription": {"type":"offer","sdp":"<RENEGOTIATION_OFFER>"},
    "tracks": [
      { "location": "local", "mid": "0", "trackName": "camera-video" },
      { "location": "local", "mid": "1", "trackName": "mic-audio"   }
    ]
  }'

# 3) 別セッションのリモートトラックをpull（購読）
curl -X POST "https://rtc.live.cloudflare.com/v1/apps/$APP_ID/sessions/xyz789/tracks/new" \
  -H "Authorization: Bearer $APP_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "tracks": [
      { "location": "remote", "sessionId": "abc123", "trackName": "camera-video" }
    ]
  }'
```

### RealtimeKit SDK 初期化（Web）
```ts
import { DyteProvider, useDyteClient } from "@dytesdk/react-web-core";
import { DyteMeeting } from "@dytesdk/react-ui-kit";

function App({ authToken }: { authToken: string }) {
  const [meeting, initMeeting] = useDyteClient();

  useEffect(() => {
    initMeeting({
      authToken,                 // バックエンドでREST API経由で発行
      defaults: { audio: true, video: true },
    });
  }, [authToken]);

  return (
    <DyteProvider value={meeting}>
      <DyteMeeting meeting={meeting!} mode="fill" />
    </DyteProvider>
  );
}
```

バックエンド側（Workers）でミーティング作成 + 参加者authToken発行：

```ts
// Cloudflare Workers
export default {
  async fetch(req, env) {
    // 1) ミーティング作成
    const meeting = await fetch("https://api.realtime.cloudflare.com/v2/meetings", {
      method: "POST",
      headers: {
        Authorization: `Basic ${btoa(`${env.RTK_ORG_ID}:${env.RTK_API_KEY}`)}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title: "Sales Call", record_on_start: false }),
    }).then(r => r.json());

    // 2) 参加者をadd → authTokenを得る
    const participant = await fetch(
      `https://api.realtime.cloudflare.com/v2/meetings/${meeting.data.id}/participants`,
      {
        method: "POST",
        headers: {
          Authorization: `Basic ${btoa(`${env.RTK_ORG_ID}:${env.RTK_API_KEY}`)}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "shogo",
          preset_name: "group_call_host",
          custom_participant_id: "user_001",
        }),
      },
    ).then(r => r.json());

    return Response.json({ authToken: participant.data.token });
  },
};
```

## 制限・注意点
- **中国本土からの接続はAnycast対象外**。中国向けプロダクトでは別経路（中国国内のWebRTCベンダ）を併用する必要がある。
- **TURN allocationごとのレート制限**：新規IP接続>5/秒、パケット>5-10kpps、帯域>50-100Mbps を超えるとパケットドロップが発生する。1人のクライアントから巨大トラフィックを流す用途（4Kマルチストリーム配信元など）は要確認。
- **E2EEは標準では非対応**。SFUは原理的にメディアを復号して再パケット化するため、E2EE要件があればInsertable Streams + アプリ層暗号化を自前で実装する必要がある。
- **録画ストレージ**：RealtimeKitの録画はR2等に払い出すまで保持期間に上限がある。長期保管は外部ストレージへのコピーをWebhookで自動化する設計が必要。
- **API rate limit**：Realtime SFUのセッション作成・トラック登録APIにはアカウント単位のレート上限がある。瞬間的な大量入室（数千人が同時接続）には事前のキャパシティ調整・段階的入室の実装が必要。
- **DataChannel経由の任意データ転送はSFUの帯域に計上される**。チャットや座標同期を高頻度で流すと、メディア帯域とは別に課金が伸びる点に注意。
- **Dyte→RealtimeKitリブランド過渡期**：SDKパッケージ名やAPIホストが`@dytesdk/*` / `api.dyte.io` から `@cloudflare/realtimekit*` / `api.realtime.cloudflare.com` 系へ移行中。最新の公式ドキュメントを参照しないと古いエンドポイントを引いて詰まる。
- **WebRTCそのものの落とし穴**は当然全部残る：エコー・ハウリング、コーデックネゴ失敗、企業FWでの443/TLS強制、モバイルのバックグラウンド時のメディア停止、Safari固有のオートプレイ制約等。Cloudflareがインフラを巻き取っても、クライアント側の実装品質は別論点。
- **料金の実測差**：1,000GB/月の無料枠は「数十人規模の社内会議用途」では十分だが、ライブ配信1万人視聴クラスではすぐに溶ける。ビットレートを下げる（720p→540p、Opus 24kbps）だけで体感品質を保ったままコストが半減することも多い。

## 参考リンク
- Cloudflare Realtime トップ：https://developers.cloudflare.com/realtime/
- Realtime SFU：https://developers.cloudflare.com/realtime/sfu/
- Realtime TURN：https://developers.cloudflare.com/realtime/turn/
- RealtimeKit：https://developers.cloudflare.com/realtime/realtimekit/
- SFU API リファレンス：https://developers.cloudflare.com/realtime/sfu/api-reference/
- Orange Meets デモ（公式リファレンス実装）：https://github.com/cloudflare/orange
- Cloudflare Calls → Realtime リブランド経緯：https://blog.cloudflare.com/cloudflare-realtime-and-realtimekit/
- Dyte 買収アナウンス：https://blog.cloudflare.com/cloudflare-acquires-dyte/
- Realtime llms.txt：https://developers.cloudflare.com/realtime/llms.txt
- Workers との連携パターン：https://developers.cloudflare.com/workers/

---
参照日: 2026-05-04
