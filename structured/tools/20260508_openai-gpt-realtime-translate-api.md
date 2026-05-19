# OpenAI gpt-realtime-translate API 検証ログ

> ステータス: 完了
> 作成日: 2026/05/08
> 最終更新: 2026/05/08
> ファイルパス: 30_プロジェクト別/knowledge-vault/vault/structured/tools/20260508_openai-gpt-realtime-translate-api.md
> 検証アプリ: 30_プロジェクト別/lab-openai-realtime-translate/

---

## 📋 検証概要

- **ツール/サービス名**: OpenAI Realtime API（`gpt-realtime-translate`）
- **検証対象**: speech-to-speech リアルタイム翻訳のWebSocket実装、言語切替、字幕/会話ログ保存
- **バージョン/リリース日**: 2026/05/07 GA（Realtime Translation / `gpt-realtime-translate`）
- **検証期間**: 2026/05/08
- **検証担当者**: shogo
- **検証ステータス**: 完了（実API接続・マイク入力・翻訳音声/字幕・会話ログ保存まで確認済み）

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- OpenAIが音声翻訳専用モデル `gpt-realtime-translate` を提供開始したため、既存のSTT→翻訳→TTS構成より低レイテンシにできるか検証した。
- 業務翻訳、ライブ配信、教育コンテンツ、多言語コミュニケーションへの適用可能性を体感ベースで判断したかった。
- Claude Codeで作成した検証アプリが「WebSocket接続・ボタン操作・マイク入力は動くが、出力言語を変えてもスペイン語になる」状態だったため、OpenAI Cookbook/Docsに照らして修正した。

### 解決したい課題
- Realtime Translationの正しいWebSocket接続方式、イベント名、セッション更新方法を把握する。
- 出力言語をUIから切り替え、実際に `session.audio.output.language` へ反映できることを確認する。
- 翻訳字幕と会話ログを検証アプリ上で確認できる状態にする。

### 期待される効果・ビジネスインパクト
- 音声翻訳デモを素早く構築できる実装知見を得る。
- 将来のNote記事、社内PoC、AI事業OSの音声AI機能検証に再利用できる。
- `$0.034/分` 程度の従量課金で、会議・配信・教育用途の翻訳体験を試せる。

---

## 2. ツール/機能の基本情報

### 概要
- `gpt-realtime-translate` は、話者音声を連続ストリームとして受け取り、翻訳音声と翻訳テキストをストリーミング返却するRealtime Translation専用モデル。
- 標準Realtime音声エージェントとは異なり、会話応答や `response.create` は使わない。モデルは「通訳」として動く。

### 提供元
- OpenAI

### 主要機能
- 70以上の入力言語を自動検出。
- 出力言語は13言語に対応: Spanish, Portuguese, French, Japanese, Russian, Chinese, German, Korean, Hindi, Indonesian, Vietnamese, Italian, English。
- `session.audio.output.language` で出力言語を指定する。
- `session.output_audio.delta` で翻訳音声、`session.output_transcript.delta` で翻訳字幕を受け取る。
- 入力書き起こしが必要な場合は `session.audio.input.transcription.model = "gpt-realtime-whisper"` を設定する。

### 技術スタック・アーキテクチャ
- Next.js 16 + React 19 + Zustand
- Custom Server: `server.ts`
- WebSocket proxy: ブラウザ → `ws://localhost:3000/api/realtime` → OpenAI
- OpenAI upstream: `wss://api.openai.com/v1/realtime/translations?model=gpt-realtime-translate`
- 音声入力: `getUserMedia` → `AudioContext(sampleRate: 24000)` → AudioWorklet → PCM16 base64
- 音声出力: `session.output_audio.delta` → AudioWorklet player → `AudioContext.destination`
- 字幕/ログ: `session.input_transcript.*` / `session.output_transcript.*` をZustandへ保存

### 価格
- 参考価格: `$0.034/分`
- 30分連続利用で約 `$1.02`

---

## 3. 検証方法

### 検証環境
- **検証アプリ**: `30_プロジェクト別/lab-openai-realtime-translate/`
- **実行環境**: macOS / Chrome / localhost
- **実行コマンド**: `pnpm dev`
- **接続方式**: サーバ側WebSocket proxy経由でOpenAI Realtime Translationへ接続
- **APIキー**: `.env.local` の `OPENAI_API_KEY` を使用（実値は記録しない）

### 検証シナリオ
1. 公式CookbookとGitHub MDXを確認する。
2. 既存実装の `server.ts`, `src/lib/realtime/*`, `MicController`, `LanguageSelector`, `store` を確認する。
3. UIで出力言語をEnglishにして録音開始する。
4. WebSocket接続、マイク入力、翻訳音声/字幕のストリーミングを確認する。
5. 出力言語がSpanish固定になる原因をサーバログ/ブラウザconsoleから切り分ける。
6. `session.updated` で `audio.output.language` が選択言語へ変わることを確認する。
7. 停止後に会話ログへ翻訳結果が残ることを確認する。

### 実行手順
1. `.env.local` に `OPENAI_API_KEY` を設定する。
2. `pnpm dev` を実行する。
3. `http://localhost:3000` を開く。
4. 出力言語を選択する。
5. `録音開始` を押し、マイク許可を与える。
6. 話しかける。
7. 翻訳音声、翻訳テキスト、入力書き起こしを確認する。
8. `停止` を押し、会話ログに入力/翻訳が残ることを確認する。

### 前提条件・制約事項
- ブラウザWebSocketは任意のAuthorizationヘッダを付けられないため、サーバ側proxyを使う。
- Realtime TranslationはGA APIとして使う。`OpenAI-Beta: realtime=v1` は付けない。
- Realtime Translationは連続ストリーム型なので、標準Realtimeの `response.create` や通常会話イベントとは異なる。

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- WebSocket proxy経由で実API接続できた。
- マイク入力をPCM16 base64として送信できた。
- 翻訳音声と翻訳字幕がストリーミング表示された。
- English出力を選ぶと英語字幕/音声が返ることを確認できた。
- 入力書き起こしと翻訳結果が会話ログに残ることを確認できた。

#### 操作性・UI/UX
- UIで出力言語を選び、録音開始/停止だけで検証できる最小構成になった。
- 波形表示により、マイク入力と翻訳音声出力の生存確認がしやすい。
- `session.updated` をconsoleへ出すことで、出力言語が正しく反映されたか確認しやすくなった。

#### 出力品質
- 短い日本語発話から英語への翻訳は自然に返った。
- 例: 日本語発話に対して `Good morning. Today is Friday!` のような英語出力を確認。
- 長文、固有名詞、専門用語、混在言語の品質評価は未実施。

#### 実用性
- PoCや社内検証用の最小アプリとしては実用可能。
- 本番用途では、セッション再接続、課金管理、音声ループバック対策、字幕のセグメント管理、複数話者対応が追加で必要。

### 定量的評価

#### 導入コスト

| 項目 | 内容 | 金額/工数 |
| --- | --- | --- |
| 初期設定時間 | Next.js + WS proxy + AudioWorklet実装 | 半日程度の検証で疎通まで到達 |
| 学習時間 | Realtime Translation固有イベントの理解 | Cookbook/Docs確認が必須 |
| 初期費用 | APIキーと従量課金のみ | 固定費なし |

#### 運用コスト

| 項目 | 内容 | 金額 |
| --- | --- | --- |
| 従量課金 | Realtime Translation利用料 | 約 `$0.034/分` |
| 30分利用 | 連続翻訳セッション | 約 `$1.02` |

#### パフォーマンス

| 項目 | 測定結果 | 備考 |
| --- | --- | --- |
| WebSocket接続 | 成功 | `/v1/realtime/translations` |
| 言語切替 | 成功 | `session.updated` で `en` を確認 |
| 音声/字幕出力 | 成功 | `session.output_audio.delta` / `session.output_transcript.delta` |
| 会話ログ保存 | 成功 | 停止/close時のflushで保存確認 |
| レイテンシ数値 | 未計測 | 体感検証のみ |

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | gpt-realtime-translate | STT→翻訳→TTS自前構成 | 人手通訳 |
| --- | --- | --- | --- |
| 実装量 | 少ない | 多い | システム実装は少ない |
| レイテンシ | 低めに期待 | 各段階の遅延が積み上がる | 品質は高いが人員依存 |
| 音声出力 | 直接返る | TTS連携が必要 | 人間音声 |
| コスト | 分課金 | 複数API課金 | 高い |
| カスタム制御 | 現時点では限定的 | 構成次第で柔軟 | 柔軟 |

### 優位性
- STT、翻訳、TTSを別々に組み合わせなくてよい。
- 低レイテンシなライブ翻訳体験を短時間で試せる。
- WebRTC/WebSocketの両方の実装パターンが公式資料で示されている。

### 劣位性・懸念点
- `gpt-realtime-translate` はカスタムpromptやvoice選択が主目的ではない。
- 出力言語は13言語に限定される。
- Realtime Translation専用イベントに合わせる必要があり、通常Realtime APIの知識だけだと誤実装しやすい。

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
| --- | --- | --- |
| APIキー管理 | 要注意 | ブラウザにAPIキーを出さず、サーバproxyまたはclient secret方式を使う |
| 音声データ | 要注意 | 会話音声を外部APIへ送るため、用途・同意・保存方針を明確化する |
| ログ管理 | 要注意 | 字幕/会話ログに個人情報が含まれる可能性がある |

### プライバシー・倫理面
- 会議・通話・配信で利用する場合は、参加者に翻訳処理と外部API送信を明示する必要がある。
- 医療・法律・金融など高リスク領域では、人間レビューや免責設計が必要。

### 技術的リスク
- ブラウザ/OSによりAudioContextのsample rate挙動が異なる可能性がある。
- 連続接続、ネットワーク断、レート制限時の復旧処理は追加検証が必要。
- `*.done` イベントに依存するとログが残らないケースがあるため、live transcriptのflush設計が必要。

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 難易度 | 備考 |
| --- | --- | --- | --- |
| ブラウザアプリ | WebRTCまたはWebSocket proxy | 中 | マイク/タブ音声を扱うならWebRTCが推奨 |
| 電話/Twilio | サーバWebSocket | 高 | 音声形式変換と双方向セッション管理が必要 |
| LiveKit | WebRTC sidecar | 高 | listenerごとに翻訳セッションを作る設計 |
| 配信/ウェビナー | listen-along translation | 中〜高 | 出力言語ごとにセッションを分ける |

### API/統合オプション
- Browser音声: WebRTC + client secret
- Backend音声: WebSocket + server-side API key
- 翻訳先言語: `session.audio.output.language`
- 入力書き起こし: `session.audio.input.transcription.model = "gpt-realtime-whisper"`

### 拡張性・カスタマイズ性
- 出力言語ごとに複数セッションを立てれば多言語配信が可能。
- 会話翻訳では、話者A→話者B言語、話者B→話者A言語の2セッション構成が必要。
- 用語集、カスタムprompt、voice選択のような高度制御は現時点では期待しすぎない方がよい。

---

## 8. 実際の使用例・サンプル

### ユースケース1: 日本語発話を英語へ翻訳

**シナリオ**: Chromeで検証アプリを開き、出力言語をEnglishにして日本語で話す。  
**入力**: マイクから日本語音声を入力。  
**出力**: 英語の翻訳音声と字幕。例: `Good morning. Today is Friday!`  
**評価**: UI選択どおり英語出力になり、会話ログにも残った。

### デバッグ時の観測ログ

`session.created` の時点では初期値として `audio.output.language: "es"` が返るが、直後の `session.updated` でUI選択値の `en` に変わることを確認した。

```text
session.created ... audio.output.language: "es"
session.updated ... audio.output.language: "en"
```

このため、「最初にcreatedでSpanishが見える」こと自体は問題ではない。最終的に `session.updated` が選択言語になっているかを見る。

---

## 9. 学びとナレッジ

### 発見したこと
- Realtime Translationは通常Realtime APIとイベント名・ライフサイクルが違う。
- 接続先は `/v1/realtime/translations?model=gpt-realtime-translate`。
- GA APIなので `OpenAI-Beta: realtime=v1` を付けるとエラーになる。
- 出力言語は `session.audio.output.language` で指定する。
- 音声入力イベントは `session.input_audio_buffer.append`。
- 出力イベントは `session.output_audio.delta` と `session.output_transcript.delta`。
- 入力書き起こしはデフォルトでは有効ではなく、`gpt-realtime-whisper` を設定する必要がある。

### うまくいったこと
- Next.js custom server + `ws` のproxy構成でブラウザからOpenAIへ安全に接続できた。
- AudioWorkletでPCM16 24kHz相当の音声チャンクを送信できた。
- UIで選択した出力言語が `session.updated` に反映された。
- 翻訳音声、翻訳字幕、会話ログ保存まで確認できた。

### うまくいかなかったこと
- 初期実装では出力言語を英語/中国語/日本語に変えてもSpanishが返っていた。
- `OpenAI-Beta: realtime=v1` を付けたことで、GA Translation APIがベータRealtime APIとして扱われ、`session.audio` がunknown parameterになった。
- UIに非対応出力言語（例: Arabic, Turkish）が含まれていた。
- 会話ログが `*.done` イベント依存だったため、ライブ表示には出るがログに残らないことがあった。

### Tips・ベストプラクティス
- Realtime Translationでは、まず `session.updated` の `audio.output.language` を確認する。
- `session.created` の初期値が `es` でも、直後に `session.updated` で選択言語へ変わっていれば問題ない。
- 出力言語UIは公式対応13言語に絞る。
- 録音中の言語変更時は `session.update` を自動送信する。
- 会話ログは `*.done` だけでなく、停止/close時にlive transcriptをflushする。
- サーバログでは音声チャンクを除外し、`session.created` / `session.updated` / `error` を中心に見る。

### よくあるエラーと対処法

| エラー | 原因 | 対処 |
| --- | --- | --- |
| `Translation sessions are only available on the GA API.` | `OpenAI-Beta: realtime=v1` を付けている | Translation endpointではBetaヘッダーを外す |
| `Unknown parameter: 'session.audio'.` | GAではなくベータ互換モードで処理されている | Betaヘッダー削除、endpoint確認 |
| 出力がSpanishになる | `session.created` の初期値だけ見ている / `session.update` 未反映 | `session.updated` の言語を見る |
| 入力書き起こしが出ない | input transcription未設定 | `gpt-realtime-whisper` を設定 |
| 会話ログが残らない | `*.done` イベント依存 | 停止/close時にlive transcriptをflush |

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️☆（4/5）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- speech-to-speech翻訳の最小検証としては、実API接続からUI操作、翻訳出力、ログ保存まで確認できた。
- 実装時の落とし穴はあるが、公式Cookbook/Docsに沿えば比較的短時間でPoC可能。
- 本番導入には、連続利用時の安定性、レイテンシ計測、プライバシー設計、複数話者設計が追加で必要。

### 次のステップ
- [ ] レイテンシを数値計測する
- [ ] 長文・固有名詞・専門用語・混在言語で品質評価する
- [ ] WebRTC client secret方式のブラウザ実装も比較する
- [ ] LiveKit/Twilioなど実ユースケース別の設計を検討する
- [x] 検証終了

### 追加で検証したい項目
- 10分以上の連続接続時の安定性
- 出力言語切替を頻繁に行った場合の挙動
- 日本語↔英語以外の言語品質
- 実コストとダッシュボード請求の突合

---

## 11. ビジネスインパクト仮説（2026/05/08追記）

### 要点
- `gpt-realtime-translate` は「翻訳アプリ」よりも広く、「リアルタイム多言語コミュニケーション機能」をあらゆるWeb/モバイルアプリへ埋め込めるAPIである。
- ブラウザ、スマホ、タブレットなど、マイク・スピーカー・ネット接続・表示UIがある端末なら成立する。専用翻訳端末の優位性は「通信込み・管理・堅牢性・業務導入のしやすさ」に寄る。
- 低リスクな対面接客、旅行、社内会議、簡易商談、教育、配信字幕では、既存の翻訳アプリ/専用端末/一部通訳業務の価格を強く押し下げる可能性がある。
- 一方で医療、法律、行政、金融、契約交渉、危機対応などは、誤訳責任・監査・本人確認・文化的含意・守秘の観点から、人間通訳/翻訳者や専門レビューの価値が残る。

### 競合環境

#### ポケトーク
- 専用端末はS2シリーズが税込36,300円〜39,930円、Sシリーズが税込19,800円〜24,800円。法人/個人向けに通信込み端末として販売されている。
- レンタルはS2で月額2,420円、S2 Plusで月額2,662円、最低6か月。
- ライブ通訳系SaaSは、個人/小規模では年額33,000円/ユーザー、チーム共有は20人まで月額33,000円〜77,000円/ライセンス、100人まで月額99,000円〜231,000円/ライセンスという価格帯。
- ポケトーク自身も「ブラウザで動く」「スマホ/タブレット/PCで使える」方向へ展開しており、専用端末だけの市場ではなくなっている。

#### DeepL Voice
- DeepL Voiceは会議/対面会話向けのリアルタイム音声翻訳を提供している。
- MeetingsはZoom/Microsoft Teams向けライブ字幕が中心で、voice-to-voiceは「coming soon」とされている。
- ConversationsはWeb/iOS/Androidで1対1会話を翻訳できる。価格はSales問い合わせ型。
- DeepLはセキュリティ、データプライバシー、企業導入を強く打ち出しており、OpenAI API直実装との差別化軸は「品質・管理・コンプライアンス・既存会議ツール統合」になりやすい。

### 置き換えられやすい業界・業務

| 領域 | 影響 | 理由 |
| --- | --- | --- |
| 旅行者向け翻訳アプリ | 大 | スマホで十分、分課金APIで音声/字幕を直接提供できる |
| 専用翻訳端末 | 中〜大 | 端末価値は残るが、スマホ/ブラウザ代替が強まる |
| 低リスクな店舗接客 | 大 | 短文・定型対応が多く、誤訳リスクを運用で吸収しやすい |
| 社内会議の簡易通訳 | 大 | 全員が母語で聞ける/読めることで会議参加障壁が下がる |
| ウェビナー/講演/教育配信 | 大 | 1つの音声を多言語字幕/音声へ展開できる |
| コールセンター一次対応 | 中〜大 | 定型問い合わせは自動化しやすいが、本人確認/苦情対応は設計が必要 |
| フリーランス翻訳の低単価案件 | 大 | AI出力＋人間のポストエディットへ単価構造が変わる |
| 医療/法律/行政通訳 | 中 | 需要は残るが、補助ツールとして浸透する可能性が高い |
| 国際商談・契約交渉 | 中 | 下準備/簡易会話は代替、最終合意や微妙な含意は人間確認が必要 |

### 新しく広がるユースケース
- 母国語しか話せない人でも、海外顧客対応、海外展示会、海外採用、越境EC、海外パートナーとの会議に参加しやすくなる。
- 日本語話者中心の中小企業でも、英語人材採用を待たずに海外営業/サポートの初動を試せる。
- 外国人労働者、観光客、留学生、医療/行政窓口利用者などに対して、最低限の多言語アクセスを提供しやすくなる。
- 配信者、講師、YouTuber、ウェビナー主催者は、1つの原音声から多言語字幕/音声を作ることで視聴可能人口を広げられる。
- 社内ナレッジ共有では、会議音声をリアルタイム翻訳しつつ、字幕ログをそのまま議事録/検索対象にできる。

### 自社/社内向けスマホアプリ化のコスト感

OpenAI API費用は `$0.034/分`。為替を1ドル150円で粗く見ると、約5.1円/分。

| 利用量 | API原価の目安 | コメント |
| --- | --- | --- |
| 10分/日 × 20営業日 | 約1,020円/月/人 | 個人の旅行・軽い接客補助ならかなり安い |
| 60分/日 × 20営業日 | 約6,120円/月/人 | 社内会議・営業同行レベル |
| 4時間/日 × 20営業日 | 約24,480円/月/人 | 通訳端末/SaaSの法人価格帯と比較対象 |
| 8時間/日 × 20営業日 | 約48,960円/月/人 | 常時通訳用途。人間通訳より安いが品質/責任設計が重要 |

アプリ開発は、既存検証コードをベースにするなら以下の感覚。

| 構成 | 初期開発 | 月額運用 | 備考 |
| --- | --- | --- | --- |
| 個人用PWA/社内PoC | 数日〜2週間 | API費用 + 数千円のホスティング | まずはWebアプリで十分 |
| 社内向けスマホWebアプリ | 2〜6週間 | API費用 + 認証/ログ基盤 | SSO、利用量制限、ログ削除が必要 |
| App Store/Google Play配布 | 1〜3か月 | API費用 + 保守 | ネイティブ音声処理、審査、課金導線が増える |
| 法人向けSaaS | 3〜6か月以上 | API費用 + 管理画面/監査/サポート | ポケトーク/DeepL Voiceと競合する領域 |

### 戦略メモ
- 個人利用では「スマホで十分」になりやすく、専用端末市場は縮小圧力を受ける。
- 法人利用では、API原価よりも「管理・セキュリティ・監査・端末配布・サポート」が価値になる。
- 参入するなら、汎用翻訳アプリ単体では競争が激しい。業界特化（医療受付、ホテル、工場、建設、教育、自治体窓口など）か、既存業務システムへの組み込みがよい。
- 人間通訳/翻訳者は消えるというより、低単価・低リスク領域がAIに寄り、高リスク/専門/文化調整/責任領域へ役割が移る可能性が高い。
- 「誰でも外国語対応できる」ことで、語学力の価値は下がる一方、専門知識・交渉力・現場判断・異文化理解の価値は上がる。

### 参考にした外部情報
- OpenAI model docs: `gpt-realtime-translate` は `$0.034/分`、Realtime Translation endpoint対応。
- OpenAI release note: 70+ input languages、13 output languages、Realtime APIで提供。
- ポケトーク公式: 専用端末価格、レンタル価格、ライブ通訳価格、ブラウザ/スマホ対応。
- DeepL Voice公式/Help: Meetings/Conversations、Zoom/Teams連携、Web/iOS/Android対応、データプライバシー方針。
- Nimdzi 100 2025: 言語サービス市場は2024年USD 71.7B、2025年USD 75.7B見込み。通訳市場は2024年USD 11.7B、2029年USD 17.1B見込み。
- Slator 2025: 言語ソリューション/技術市場をUSD 31.70Bと見積もり、live interactionsを含む言語AI市場の拡大を示唆。

---

## 12. 公開・本番化アーキテクチャ方針（2026/05/08追記）

### ローカル検証で作った構成

今回の検証アプリは、ブラウザとOpenAIの間に自前Node.jsサーバを置くWebSocket proxy構成。

```text
ブラウザ/PC
  ↕ WebSocket
Next.js custom server / Node.js
  ↕ WebSocket
OpenAI Realtime Translation API
```

この方式は仕組みの理解とデバッグには向いている。ブラウザからOpenAIへ直接APIキーを渡さずに済み、サーバログで `session.created` / `session.updated` / `error` を追える。

一方で、公開アプリとして運用する場合は、自前Node.jsサーバがクライアント接続とOpenAI接続の両方を長時間保持する。そのため、通常のリクエスト/レスポンス型ホスティングではなく、WebSocketを保持できる実行環境が必要になる。

### 短期公開PoCの候補

| 候補 | 判定 | 理由 |
| --- | --- | --- |
| Render Web Service | 有力 | WebSocket対応。Node.js/Express/ws構成をそのまま載せやすい |
| Google Cloud Run | 有力 | WebSocket対応。Docker化しやすく、スケール/HTTPSも扱いやすい。ただしrequest timeoutと再接続設計が必要 |
| Railway | 次点 | WebSocket対応。ただし接続時間制限や再接続設計を前提にする |
| さくらVPS | 可能 | Node.js/Docker/Nginxを自分で管理できる。運用負荷は高め |
| Fly.io / EC2 / Lightsail | 可能 | 常駐プロセスを持てるため相性はよい |

現時点の方針としては、素早く外部公開してスマホ実機で試すなら **Render** または **Google Cloud Run** を第一候補にする。

### 避けたい/不向きな候補

| 候補 | 判定 | 理由 |
| --- | --- | --- |
| Vercel Functions | 不向き | Serverless FunctionsはWebSocket常時接続を保持できない。Streaming/SSEとWebSocketは別物 |
| さくらのレンタルサーバ | 不向き | 共用サーバであり、常駐Node.js/WebSocket proxy用途には向かない |
| 一般的なPHP共用レンタルサーバ | 不向き | 常時接続、Node.jsプロセス、リバースプロキシ管理が難しい |

VercelはNext.jsの静的/通常Webアプリには強いが、今回のNode.js WebSocket proxyをそのまま載せる場所ではない。使うなら、フロントエンドだけVercel、Realtime中継はRender/Cloud Runのように分ける。

### 本番プロダクトでの推奨構成

スマホ/ブラウザ向け本番アプリでは、OpenAI公式が推奨する **WebRTC + client secret方式** に寄せるのが自然。

```text
スマホ/ブラウザ
  ↕ WebRTC
OpenAI Realtime API

自前バックエンド
  → 短命client secretを発行するHTTP endpointのみ
```

この構成では、自前バックエンドが長時間WebSocketを中継しない。サーバはOpenAI APIキーを安全に保持し、ブラウザに短命client secretを渡すだけになる。

メリット:
- モバイルブラウザの音声通信に向いている
- 自前サーバのWebSocket接続数/帯域負荷を抑えられる
- Vercelなどのserverless環境でもclient secret発行APIだけなら実装しやすい
- レイテンシ面でもWebSocket proxyより有利になりやすい

注意点:
- WebRTC実装へ作り替える必要がある
- セッション発行APIに認証、レート制限、利用量制限を付ける必要がある
- モバイルSafari/Chromeのマイク許可、音声再生、自動再生制限を検証する必要がある
- 翻訳ログを保存したい場合、クライアント側イベントまたは別APIで保存設計が必要

### 段階的な進め方

1. **現行WebSocket proxyをRender/Cloud Runへ載せる**
   - 目的: 外部URLでスマホ実機検証する。
   - 確認: HTTPS/WSS、マイク許可、音声出力、会話ログ、接続切断/再接続。

2. **公開PoCとして最低限の保護を入れる**
   - 簡易認証
   - 1セッションの最大時間
   - 利用量ログ
   - APIキー漏洩防止
   - エラー時の自動切断

3. **WebRTC + client secret方式へ移行検証**
   - 目的: スマホ/ブラウザ向けの本番候補構成へ寄せる。
   - サーバはtoken発行とログ保存に限定する。

4. **本番化判断**
   - 個人/社内PoCならWebアプリで十分。
   - 法人向けなら、認証、監査ログ、利用制限、会話データ削除、管理画面が必要。
   - App Store/Google Play配布は、Web PoCで価値検証後に判断する。

### 実運用で必要な設計項目

- HTTPS/WSS対応
- APIキーのサーバ側管理
- ユーザー認証
- セッション単位の時間制限
- 利用量/課金ログ
- WebSocket/WebRTC切断時の再接続
- ping/pong keepalive
- エラー時の明示表示
- 会話ログの保存/削除ポリシー
- 個人情報/機密情報を扱う場合の同意導線
- モバイルブラウザのバックグラウンド/画面ロック時の挙動確認

### 現時点の判断

- **最短で外部公開する**: RenderまたはGoogle Cloud Run。
- **Next.jsフロントを綺麗に公開する**: Vercel + 別Realtimeサーバ。
- **スマホ向け本番を見据える**: WebRTC + client secret方式。
- **さくらを使うなら**: レンタルサーバではなくVPS/クラウド。

---

📚 関連リソース

### 公式ドキュメント
- [Realtime translation | OpenAI API](https://developers.openai.com/api/docs/guides/realtime-translation)
- [Build Live Translation Apps with gpt-realtime-translate | OpenAI Cookbook](https://developers.openai.com/cookbook/examples/voice_solutions/realtime_translation_guide)
- [GitHub: realtime_translation_guide.mdx](https://github.com/openai/openai-cookbook/blob/main/examples/voice_solutions/realtime_translation_guide.mdx)
- [Realtime API with WebRTC | OpenAI API](https://platform.openai.com/docs/guides/realtime-webrtc)

### 参考記事・事例
- [Advancing voice intelligence with new models in the API | OpenAI](https://openai.com/index/advancing-voice-intelligence-with-new-models-in-the-api/)
- [Realtime API with WebSocket | OpenAI Docs](https://developers.openai.com/api/docs/guides/realtime-websocket)
- [gpt-realtime-translate model page | OpenAI API](https://developers.openai.com/api/docs/models/gpt-realtime-translate)
- [Vercel: Do Vercel Serverless Functions support WebSocket connections?](https://vercel.com/guides/do-vercel-serverless-functions-support-websocket-connections)
- [Render: WebSockets on Render](https://render.com/docs/websocket)
- [Railway: Deploy a WebSocket Application with Socket.IO](https://docs.railway.com/guides/socketio)
- [Google Cloud Run: Using WebSockets](https://docs.cloud.google.com/run/docs/triggering/websockets)
- [Cloudflare Workers: WebSockets](https://developers.cloudflare.com/workers/runtime-apis/websockets/)
- [ポケトーク公式: AI通訳機ポケトーク](https://pocketalk.jp/device)
- [ポケトーク公式: ライブ通訳 ご購入ページ](https://pocketalk.jp/forbusiness/livetranslation/biz_purchase)
- [ポケトーク公式: Sentio / AI同時通訳サービス](https://pocketalk.jp/software/)
- [DeepL Voice](https://www.deepl.com/en/products/voice)
- [DeepL Voice for Meetings](https://www.deepl.com/en/products/voice/deepl-voice-for-meetings)
- [Nimdzi 100 2025](https://www.nimdzi.com/nimdzi-100-2025/)
- [Nimdzi Interpreting Index 2025](https://www.nimdzi.com/interpreting-index/)
- [Slator 2025 Language Industry Market Report](https://slator.com/slator-2025-language-industry-market-report/)

### 社内関連ドキュメント
- `30_プロジェクト別/lab-openai-realtime-translate/`
- `30_プロジェクト別/knowledge-vault/vault/structured/tools/20250823_realtime-voice-subtitle-translation.md`

### 検証データ・ログ
- 検証アプリ内の会話ログ
- Chrome DevTools console
- `pnpm dev` 実行時のサーバログ

---

✅ メモ・議論ログ

- Claude Codeで作成した初期実装は、WebSocket、ボタン、マイク入力までは動いていた。
- 問題は出力言語を変更してもSpanishが返る点だった。
- 公式CookbookとGitHub MDXを確認し、Translation専用endpoint、GA API、イベント名の差分を確認した。
- `OpenAI-Beta: realtime=v1` が原因でGA Translation APIが正しく扱われていなかった。
- Betaヘッダー削除後、`session.created` → `session.updated` の流れで出力言語がEnglishへ更新されることを確認した。
- 会話ログ未保存は `*.done` 依存が原因だったため、停止/close時にlive transcriptを保存する設計へ変更した。
- 最終的に、正しく翻訳され、会話ログも残ることをユーザー側で確認した。

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/05/08 | ファイル作成（init） |
| 2026/05/08 | 実API接続後の不具合修正・動作確認結果を反映し、検証完了として整理 |
| 2026/05/08 | リアルタイム翻訳AIの市場インパクト、競合、スマホアプリ化コスト仮説を追記 |
| 2026/05/08 | 外部公開・本番化を見据えたWebSocket/WebRTC構成方針を追記 |
