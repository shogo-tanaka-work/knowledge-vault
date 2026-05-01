# STT API 比較・使い分けガイド（決定版）

**最終更新**: 2026-05-01  
**対象読者**: 音声認識（STT）APIを選定・導入したい開発者・受講生

---

## このドキュメントの読み方

```
個人情報・医療カルテ等を扱わない場合
→ セクション1〜3だけ読めばOK

個人情報・カルテデータを扱う場合
→ セクション4〜8も必読
```

---

## 結論（2026年5月時点）

| 目的 | 推薦サービス |
|-----|------------|
| **新規プロジェクト・日本語精度重視** | **ElevenLabs Scribe v2** |
| OpenAI互換のまま安くしたい | Groq Whisper v3 Turbo |
| 個人情報・カルテを含む音声 | ローカルOSSまたは国産オンプレ |

> **ゼロベースで始めるなら ElevenLabs Scribe v2 が現時点のベストチョイス。**  
> 日本語WER 2.2%（業界最高）、コスト $0.0037/分、リアルタイム150ms、日本語「Excellent」公式保証。

---

## 1. クラウドSTT API 比較

### コスト（1分あたり）

| サービス | バッチ | ストリーミング | 備考 |
|---------|:-----:|:-----------:|------|
| **ElevenLabs Scribe v2** | $0.0037 | ✕ | バッチ専用。精度業界最高 |
| **ElevenLabs Scribe v2 Realtime** | — | $0.0065 | リアルタイム専用。150ms |
| **Groq Whisper v3 Turbo** | $0.00067 | ✕ | OpenAI完全互換。最安バッチクラス |
| **fal.ai Wizper** | $0.0005 | ✕ | 最安値。バッチ特化 |
| **Deepgram Nova-3** | $0.0043 | $0.0077 | 低レイテンシ・日英混在対応 |
| **AssemblyAI Universal-2** | $0.0045 | $0.0025 | 話者分離等機能追加は別料金 |
| **Gladia Solaria-1** | $0.0041〜 | $0.0042〜 | ミーティング文字起こし特化 |
| **OpenAI gpt-4o-transcribe** | $0.006 | $0.006 | バッチ・ストリーミング両対応 |
| **OpenAI gpt-4o-mini-transcribe** | $0.003 | $0.003 | 2025年12月以降に改善済み |
| **OpenAI whisper-1** | $0.006 | ✕ | レガシー。新規開発では非推奨 |
| **Google STT v2 (Dynamic Batch)** | $0.003 | $0.016 | 大量バッチに有利 |
| **Azure Speech** | $0.006 | $0.0167 | 5時間/月無料枠。日本リージョンあり |
| **Amazon Transcribe** | $0.024 | $0.024 | 割高・15秒最低課金。学習利用に注意 |
| **Rev.ai** | $0.003 | — | 日本語は外国語モデル扱い ($0.005) |

### レイテンシー（ストリーミング対応サービス）

| サービス | レイテンシー | 品質 |
|---------|:---------:|:---:|
| **Gladia Solaria-1** | **103ms**（partials） | ◎ |
| **ElevenLabs Scribe v2 Realtime** | **150ms** | ◎ |
| OpenAI Realtime API | ~232ms（不安定報告あり） | ○ |
| Deepgram Nova-3 | <300ms | ◎ |
| AssemblyAI | ~300ms | ○ |
| Google STT v2 | ~350ms | ◎ |
| Azure Speech | ~450ms | ◎ |
| Amazon Transcribe | 600〜800ms | ○ |

### 日本語精度（WER：低いほど高精度）

| サービス | 日本語WER | 出典 |
|---------|:--------:|------|
| **ElevenLabs Scribe v2** | **2.2%** | Artificial Analysis 2025〜2026年 |
| Soniox | 8.7% | 自社主催ベンチマーク（バイアス注意） |
| Groq / fal.ai Wizper | ~5〜8% | Whisper large-v3相当 |
| Deepgram Nova-3 | 11.7% | Soniox 2025年版 |
| OpenAI gpt-4o-transcribe | 13.8% | Soniox 2025年版 |
| Azure Speech | 14.0% | Soniox 2025年版 |
| Google STT | 14.2% | Soniox 2025年版 |
| AssemblyAI | 14.8% | Soniox 2025年版 |
| Amazon Transcribe | 16.2% | Soniox 2025年版 |

---

## 2. 推薦：ElevenLabs Scribe v2 を選ぶ理由

### 強み

| 観点 | 評価 | 補足 |
|------|:----:|------|
| 日本語精度 | ◎ | WER 2.2%。業界最高。「Excellent（WER≤5%）」を公式保証 |
| コスト | ◎ | $0.0037/分。OpenAI比40%安、Amazon比85%安 |
| リアルタイム | ◎ | Scribe v2 Realtime で150ms（2025年11月〜） |
| 話者分離 | ◎ | 最大32名まで対応。追加料金なし |
| 多言語 | ◎ | 99言語対応 |

### 弱み・トレードオフ

| 観点 | 評価 | 補足 |
|------|:----:|------|
| OpenAI互換 | ✕ | 独自APIスキーマ。既存のOpenAI SDKコードは移行作業が必要 |
| データ処理地 | ✕ | 日本リージョンなし。音声データは米国処理 |
| エコシステム | △ | OpenAIと比べて日本語の事例・記事が少ない |
| 個人情報・医療データ | ✕ | 通常プランはNG。→ セクション4・7参照 |

### OpenAI APIとの比較まとめ

| 観点 | ElevenLabs Scribe v2 | OpenAI gpt-4o-transcribe |
|-----|:------------------:|:----------------------:|
| 日本語WER | **2.2%** | 13.8% |
| バッチコスト | **$0.0037** | $0.006 |
| リアルタイムレイテンシー | **150ms** | ~1,598ms |
| OpenAI互換 | ✕ | ◎ |
| 日本語品質の公式保証 | **◎ 明示** | △ 言及なし |

> **ゼロベースの新規実装であれば、すべての観点でElevenLabsが上回る。**  
> 既存コードがOpenAI SDK前提の場合は、Groq Whisper（OpenAI互換・$0.00067/分）への移行が現実的。

---

## 3. ユースケース別推薦

| ユースケース | 推薦 | 理由 |
|------------|------|------|
| **新規・日本語精度重視（個人情報なし）** | **ElevenLabs Scribe v2** | WER 2.2%・コスト・リアルタイム全方位最良 |
| OpenAI互換のまま移行したい | **Groq Whisper v3 Turbo** | $0.00067/分・エンドポイントURLを変えるだけ |
| バッチ処理・コスト最安 | **fal.ai Wizper** | $0.0005/分・250x realtime速度 |
| リアルタイム会話・コールセンター | **ElevenLabs Scribe v2 Realtime** | 150ms・話者分離32名 |
| ミーティング・会議文字起こし | **Gladia Solaria-1** | partials 103ms・話者分離込み |
| 大量バッチ（コスト最優先） | **Google STT v2 Dynamic Batch** | $0.003/分で最安水準 |
| 日本国内データ処理必須 | **Azure Speech (Japan East)** | APPI対応・国内処理が最も明確 |
| 個人情報・カルテ含む音声 | **ローカルOSS or 国産オンプレ** | → セクション4〜8参照 |

---

## 4. ローカルモデルが必要な判断基準

> **個人情報・医療カルテ等を扱わない場合、このセクション以降は読み飛ばしてOKです。**

### ローカルを選ぶべき3つのケース

```
1. 音声データに個人情報・要配慮個人情報が含まれる
   （医療カルテ、金融相談、弁護士相談 など）

2. 法的にデータを国外に出せない
   （厚労省ガイドライン第6.0版・APPI対応が必要）

3. 月100時間以上の大量処理でTCO最小化したい
   （月100時間超でローカルGPUがクラウドAPIより安くなる）
```

### 法的根拠

**厚生労働省「医療情報システムの安全管理ガイドライン第6.0版」（2023年5月）**
- 音声データは**要配慮個人情報**（患者情報）に該当
- クラウド利用時は「データ処理場所の明示」と「責任分界を書面化」が必須

**APPI（個人情報保護法）改正動向**
- 2025年審議中・**2027年施行見込み**
- 音声データが「生体データ」として特別カテゴリに分類される可能性あり
- ElevenLabs・OpenAI等すべての米国クラウドAPIが同様に規制対象

---

## 5. ローカルデプロイ可能なOSSモデル比較

### GPU環境向け

| モデル | 日本語精度(CER) | 速度 | 最小GPU | ライセンス | 特徴 |
|--------|:------------:|:----:|:------:|:--------:|------|
| **Whisper large-v3** | 8.5% | 標準 | RTX 3060(12GB) | MIT | 精度最高水準・多言語 |
| **Whisper large-v3-Turbo** | 8.8% | 5.4倍速 | RTX 3060(6GB) | MIT | 精度ほぼ同等・大幅高速化 |
| **faster-whisper (INT8量子化)** | 同等 | 4倍速 | RTX 3060 | MIT | VRAM削減・**実運用の推奨** |
| **kotoba-whisper v2.2** | 9.2% | 6.3倍速 | RTX 3060(8GB) | Apache 2.0 | 日本語特化・話者分離統合。専門用語は要評価 |
| **ReazonSpeech v2** | 高（非公開） | 低速 | — | Apache 2.0 | 日本語720万件学習 |

**GPU環境での推奨**: `faster-whisper large-v3 INT8`

### GPUなし環境（CPU / Apple Silicon）

> **GPUがなくてもWhisper系は動く。環境によって速度差が大きい。**

#### Apple Silicon（M1以降）— 実用的

| チップ | 10分音声の処理時間 | RTF |
|--------|:---------------:|:---:|
| M1（MacBook Air） | 約3分 | 0.30x |
| M1 Pro | 約2分 | 0.20x |
| M2（MacBook Air） | 約2.5分 | 0.25x |
| M3 Pro | 約1.5分 | 0.15x |
| M4 Pro | 約50秒 | 0.08x |

RTF < 1.0 = リアルタイムより速い。**M1でも十分実用的。**

- 推奨ツール: **mlx-whisper**（M1 Pro で 29.7x realtime・最速）
- faster-whisper は NVIDIA GPU 前提のため Apple Silicon では非効率

#### x86 CPU（Windows/Linux）

| モデル | 推奨度 | 備考 |
|--------|:-----:|------|
| tiny / base | △ | 高速だが精度が低い |
| **small** | ◎ | **CPU専用の実用ライン**（RTF ~0.1〜0.2） |
| medium（量子化） | △ | ハイエンドCPUなら許容（RTF ~0.3〜0.5） |
| large-v3（量子化なし） | ✕ | RTF ~2.5以上・CPU単独では非現実的 |

ツール: `whisper.cpp`（AVX2/AVX-512対応CPUで高速。Windowsビルド済みバイナリあり）

#### 超低スペック端末（Raspberry Pi等）

| ツール | 最小スペック | RTF | 特徴 |
|-------|:---------:|:---:|------|
| **Vosk** | Raspberry Pi 3B+ | ~1.0x | 50MB〜。精度はWhisperより劣る |
| **sherpa-onnx** | Raspberry Pi 4 (1GB RAM) | <0.2x | int8モデルで200ms以下 |
| **Moonshine**（2026年2月〜） | 低リソース設計 | 未計測 | 低リソース向け・Whisper超精度を主張 |

### ローカル運用コスト目安（月500時間処理の場合）

| 選択肢 | 月額コスト | 初期費用 |
|-------|:--------:|:-------:|
| ElevenLabs Scribe v2 | ~$1,110/月 | なし |
| OpenAI gpt-4o-transcribe | ~$1,800/月 | なし |
| ローカル（RTX 4090購入） | 電気代+保守のみ | ~$2,000 |
| GPUクラウドインスタンス借用 | ~$200〜250/月 | なし |

---

## 6. ローカルモデルをAPIとして公開する方法

### デプロイパターン3種

```
① セルフホスト（オンプレ or VPS）
   自前サーバー or クラウドVM に Docker でデプロイ
   → データが外に出ない。医療用途に最適。

② GPU特化クラウド（RunPod / Modal / Fly.io）
   GPU環境をマネージドで借りてデプロイ
   → インフラ管理不要・コスト安。ただしデータは外部へ。

③ 大手クラウド（AWS / GCP / Azure）
   SageMaker / Hugging Face Endpoints 等
   → エンタープライズ向け。HIPAA対応は個別確認要。
```

### ① セルフホスト：OSSサーバーフレームワーク比較

| サーバー名 | OpenAI互換API | ストリーミング | Docker | 推薦度 |
|-----------|:-----------:|:-----------:|:------:|:------:|
| **Speaches**（旧faster-whisper-server） | ◎ | SSE + WebSocket | ◎ | ★★★ |
| **whisper-asr-webservice** | ◎ | 一部 | ◎ | ★★★ |
| **docker-whisper**（hwdsl2） | ◎ | SSE | ◎ | ★★ |
| **LocalAI** | ◎ | ◎ | ◎ | ★★ |
| **WhisperX API Server** | ◎ | ◎ | ○ | ★★（話者分離が必要な場合） |
| **whisper.cpp** | ○ | 限定的 | ○ | ★（軽量端末向け） |

### 本命：Speaches（speaches-ai/speaches）

- `docker-compose up` 1コマンドで起動
- OpenAIの `/v1/audio/transcriptions` と完全互換
- 既存のOpenAI SDKコードをエンドポイントURLの変更だけで流用可能

```python
from openai import OpenAI

client = OpenAI(api_key="dummy", base_url="http://localhost:8000")

with open("audio.mp3", "rb") as f:
    result = client.audio.transcriptions.create(
        model="Systran/faster-whisper-large-v3",
        file=f
    )
print(result.text)
```

### ② GPU特化クラウド

| プラットフォーム | 特徴 | コスト目安 | 難易度 |
|--------------|------|:--------:|:------:|
| **RunPod** | 公式worker（`worker-faster_whisper`）あり | $0.0002〜/リクエスト | ★ |
| **Modal.com** | Pythonコードだけでデプロイ・オートスケール | $0.0001〜/リクエスト | ★ |
| **Replicate** | GUIでデプロイ・APIキーだけで呼べる | $0.0023/分 | ★ |
| **Hugging Face Inference Endpoints** | GUIでモデル選んでデプロイ | $0.006〜/時間 | ★ |

### ③ 大手クラウド（VPC内クローズド処理）

| クラウド | サービス | 特徴 |
|---------|---------|------|
| **AWS** | SageMaker + JumpStart | Whisper large-v3が公式サポート済み。VPC内処理可 |
| **Azure** | Container Apps（Japan East） | DockerイメージそのままデプロイOK。APPI対応明確 |
| **GCP** | Cloud Run（GPU） | サーバーレスGPUで運用可 |

---

## 7. データプライバシー・学習利用ポリシー

### 「API経由なら学習に使われない」は半分正しい

| 観点 | 実態 |
|-----|------|
| 学習への利用 | ✅ API経由はデフォルトで学習に使われない（OpenAI・ElevenLabs共通） |
| ログの保持 | ⚠️ OpenAIはデフォルト最大30日間保持される |
| ゼロ保持（ZDR） | OpenAI Enterprise/Businessプランで申請可 |

### 個人情報・カルテデータをAPIに送っていいか

| ケース | 判断 |
|-------|:----:|
| 個人情報なし（講義録音・会議メモ等） | ✅ 通常のAPI利用でOK |
| 氏名・連絡先程度が含まれる | ⚠️ APPI越境移転同意の確認が必要 |
| 医療カルテ・診察音声 | ❌ 通常プランはNG。ZDR+BAA+APPI対応が必要 |

> **ElevenLabs・OpenAI・Groq等、すべての米国クラウドAPIでこの判断基準が同様に適用される。**

### 医療データをクラウドAPIで合法的に扱う3条件

```
① ZDR（ゼロデータリテンション）を有効化
   → Enterprise/Businessプランで個別申請

② BAA（Business Associate Agreement）を締結
   → OpenAI: baa@openai.com に申請
   → ElevenLabs: 要問い合わせ

③ 日本APPIの越境移転要件を満たす
   → 本人同意の取得、または十分な安全管理措置の整備
```

### 各クラウドSTT APIのデータポリシー比較

| サービス | デフォルト学習利用 | ログ保持 | 医療データ対応 |
|---------|:--------------:|:-------:|:-----------:|
| **OpenAI API** | なし | 30日（ZDRで0日） | 条件付き可 |
| **ElevenLabs** | なし | 要確認 | BAA要問い合わせ |
| **Azure Speech** | なし | リアルタイムは非保存 | ◎ Japan East + BAA整備済み |
| **Google Cloud STT** | なし | 同期/ストリーミングは非保存 | △ 要個別確認 |
| **AWS Transcribe** | **あり（要オプトアウト）** | 要確認 | △ HIPAA対応だが日本語医療は限定的 |

> **AWSのみ「デフォルトで学習に使われる」設定。**オプトアウトはAWS Organizations ポリシーで可能。

### 日本法上の注意点（APPI）

- APPI第28条：米国等の第三者への個人データ移転は原則**本人の事前同意**が必要
- 個人情報保護委員会が2023年にOpenAIへ公式警告を発出済み
- 音声データには声紋（生体情報）が含まれる場合があり、**要配慮個人情報**として一層厳格な規制対象
- 2026〜2027年施行予定のAPPI改正で越境移転違反への**行政加算金**が新設予定

---

## 8. 医療・個人情報用途の選択フロー

```
音声データに個人情報・カルテ情報が含まれる？
│
├── YES
│   ├── クラウドAPIで対応したい
│   │   ├── ZDR + BAA 取得可能 → Azure Speech (Japan East) が最も整備済み
│   │   └── 取得困難 or リスク回避 → ローカル or 国産オンプレへ
│   │
│   ├── 自社サーバーあり（オンプレ）
│   │   → Speaches + faster-whisper をDockerデプロイ
│   │
│   └── 国産サポート・SLAが必要
│       → AmiVoice iNote / mocoVoice医療モデル
│
└── NO（個人情報なし・一般用途）
    ├── 新規・日本語精度重視 → ElevenLabs Scribe v2  ← 大抵これでOK
    ├── OpenAI互換コード流用 → Groq Whisper v3 Turbo
    ├── バッチ最安値 → fal.ai Wizper
    ├── リアルタイム会話 → ElevenLabs Scribe v2 Realtime
    └── ミーティング文字起こし → Gladia Solaria-1
```

---

## 9. 国産・医療特化商用サービス（参考）

| サービス | 形態 | 日本語特化 | 医療対応 | 特徴 |
|---------|:----:|:--------:|:-------:|------|
| **AmiVoice iNote** | 院内オンプレ設置型 | ◎ 診療科別辞書 | ◎ | 月額3,300円〜 |
| **AmiVoice API Private** | 専用クラウド/オンプレ | ◎ | ◎ | 金融・医療向け。ISMS取得 |
| **mocoVoice医療モデル** | オンプレ専用 | ◎ 医療用語10万語 | ◎ | 2025年3月リリース。IT補助金対象 |

---

## 参考リンク

- [ElevenLabs Speech-to-Text 公式](https://elevenlabs.io/speech-to-text)
- [ElevenLabs Scribe v2 Realtime](https://elevenlabs.io/realtime-speech-to-text)
- [Artificial Analysis STT Leaderboard](https://artificialanalysis.ai/speech-to-text)
- [Groq STT ドキュメント](https://console.groq.com/docs/speech-to-text)
- [fal.ai Wizper モデルページ](https://fal.ai/models/fal-ai/wizper)
- [Gladia リアルタイムSTT](https://www.gladia.io/product/real-time)
- [Soniox STT Benchmarks 2025](https://soniox.com/benchmarks)
- [Zenn：2025年日本語STT比較](https://zenn.dev/hongbod/articles/def04f586cf168)
- [Neosophie：2026年版IT用語ASRベンチマーク（Qwen3-ASR vs Whisper）](https://neosophie.com/ja/blog/20260414-it-asr-benchmark)
- [Calm-Whisper：ハルシネーション80%削減（arXiv 2025-05）](https://arxiv.org/abs/2505.12969)
- [Apple Silicon Whisper速度ベンチマーク](https://www.voicci.com/blog/apple-silicon-whisper-performance.html)
- [mlx-whisper vs faster-whisper on Apple Silicon](https://medium.com/@GenerationAI/streaming-with-whisper-in-mlx-vs-faster-whisper-vs-insanely-fast-whisper-37cebcfc4d27)
- [GitHub - speaches-ai/speaches](https://github.com/speaches-ai/speaches)
- [GitHub - whisper.cpp](https://github.com/ggml-org/whisper.cpp)
- [sherpa-onnx（エッジデバイス向けSTT）](https://www.blog.brightcoding.dev/2025/09/11/sherpa-onnx-unified-speech-recognition-synthesis-and-audio-processing-for-every-platform/)
- [kotoba-whisper-v2.2 on Hugging Face](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.2)
- [OpenAI データ管理ポリシー（公式）](https://developers.openai.com/api/docs/guides/your-data)
- [OpenAI BAA申請方法](https://help.openai.com/en/articles/8660679-how-can-i-get-a-business-associate-agreement-baa-with-openai)
- [Azure Speech データプライバシー（公式）](https://learn.microsoft.com/en-us/legal/cognitive-services/speech-service/speech-to-text/data-privacy-security)
- [AWS Transcribe 学習利用オプトアウト（公式）](https://docs.aws.amazon.com/transcribe/latest/dge/opt-out.html)
- [厚労省 医療情報システム安全管理ガイドライン第6.0版](https://www.mhlw.go.jp/stf/shingi/0000516275_00006.html)
- [個人情報保護委員会 生成AIサービスに関する注意喚起（2023年）](https://www.ppc.go.jp/news/careful_information/230602_AI_utilize_alert/)
