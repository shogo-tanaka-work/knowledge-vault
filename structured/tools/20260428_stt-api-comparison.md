# STT API 比較・使い分けガイド（2025〜2026年版）

**対象読者**: 音声認識（STT）APIを選定・導入したい開発者・受講生  
**最終更新**: 2026-04-28

---

## このドキュメントの読み方

```
個人情報・医療カルテ等を音声処理する予定がない場合
→「ローカルLLMが必要な判断基準」セクションは読み飛ばしてOK
→「クラウドSTT API比較」→「推薦：Whisperを選ぶ理由」だけ読めば十分
```

---

## 1. クラウドSTT API 比較

### コスト（1分あたり）

| サービス | バッチ | ストリーミング | 備考 |
|---------|-------|------------|------|
| **OpenAI whisper-1** | $0.006 | ✕ 非対応 | バッチ処理専用 |
| **OpenAI gpt-4o-mini-transcribe** | $0.003 | $0.003 | 2025年12月〜。最安OpenAI |
| **OpenAI gpt-4o-transcribe** | $0.006 | $0.006 | Realtime API経由 |
| **Google STT v2 (Dynamic Batch)** | $0.003 | $0.016 | 大量バッチに有利 |
| **Azure Speech** | $0.006 | $0.0167 | 5時間/月無料枠あり |
| **Amazon Transcribe** | $0.024 | $0.024 | 15秒最低課金・割高 |
| **Deepgram Nova-3** | $0.0043 | $0.0077 | 低レイテンシ特化 |
| **AssemblyAI Universal-2** | $0.0045 | $0.0025 | 機能追加は別料金 |
| **Rev.ai** | $0.003 | — | 日本語はForeignモデル($0.005) |

### レイテンシー（ストリーミング）

| サービス | 参考レイテンシー | ストリーミング |
|---------|--------------|:-----------:|
| Deepgram Nova-3 | <300ms（最速クラス） | ◎ |
| OpenAI Realtime API | ~232ms（不安定報告あり） | ○ |
| Google STT v2 | ~350ms | ◎ |
| Azure Speech | ~450ms | ◎ |
| AssemblyAI | ~300ms | ○ |
| Amazon Transcribe | 600〜800ms | ○ |
| **whisper-1** | **N/A（バッチのみ）** | ✕ |

### 日本語精度（WER：低いほど高精度）

Soniox社ベンチマーク2025年版（YouTube実音声・二重チェック済み）

| サービス | 日本語WER |
|---------|:--------:|
| Soniox | 8.7%（自社主催バイアス注意） |
| Deepgram Nova-3 | 11.7% |
| **OpenAI gpt-4o-transcribe** | **13.8%** |
| Azure Speech | 14.0% |
| Google STT | 14.2% |
| AssemblyAI | 14.8% |
| Amazon Transcribe | 16.2% |

---

## 2. 推薦：Whisper（OpenAI API）を選ぶ理由

### 強み

| 観点 | 評価 | 補足 |
|------|:----:|------|
| コスト | ◎ | $0.006/分。Amazonの75%安。Azure・Googleと同水準 |
| 日本語対応 | ◎ | 100+言語対応、日英混在コンテンツに強い |
| 導入の容易さ | ◎ | REST API一本。SDK充実。インフラ不要 |
| 進化余地 | ◎ | gpt-4o-mini-transcribeで$0.003/分・精度向上（2025年12月〜） |
| エコシステム | ◎ | 日本語コミュニティ・事例が最も豊富 |

### 弱み・トレードオフ

| 観点 | 評価 | 補足 |
|------|:----:|------|
| リアルタイム | △ | whisper-1はバッチのみ。Realtime API（gpt-4o-transcribe）は別途必要 |
| データ処理地 | ✕ | 日本リージョンなし。音声データは米国処理 |
| 最高精度 | △ | WER 13.8%。Deepgram(11.7%)には劣る |

### 一言まとめ

> **最安でも最高精度でもないが、コスト・品質・使いやすさのどの観点でも合格点を出せる唯一の選択肢。**  
> 特定要件（超低レイテンシ・国内処理必須・最高精度）がなければ、最初に選ぶべき標準解。

---

## 3. ユースケース別推薦

| ユースケース | 推薦 | 理由 |
|------------|------|------|
| 汎用バッチ文字起こし（個人情報なし） | **OpenAI whisper-1 / gpt-4o-mini-transcribe** | バランス最良 |
| リアルタイム会話・コールセンター | **Deepgram Nova-3** | <300msレイテンシ、日英混在対応 |
| 大量バッチ（コスト最優先） | **Google STT v2 Dynamic Batch** | $0.003/分で最安水準 |
| 日本国内データ処理必須 | **Azure Speech (Japan East)** | APPI対応・国内処理明確 |
| 日本語精度最優先 | **Deepgram Nova-3** | WER 11.7% |

---

## 4. ローカルLLMが必要な判断基準

> **個人情報・医療カルテ等を音声処理する予定がない場合、このセクションは読み飛ばしてOKです。**

### ローカルを選ぶべき3つのケース

```
1. 音声データに個人情報・要配慮個人情報が含まれる
   （医療カルテ、金融相談、弁護士相談 など）

2. 法的にデータを国外に出せない
   （厚労省ガイドライン第6.0版・APPI対応が必要）

3. 月100時間以上の大量処理でTCO最小化したい
   （クラウドAPIより安くなる分岐点）
```

### 法的根拠

**厚生労働省「医療情報システムの安全管理ガイドライン第6.0版」（2023年5月）**
- 音声データは**要配慮個人情報**（患者情報）に該当
- クラウド利用時は「データ処理場所の明示」と「責任分界を書面化」が必須

**APPI（個人情報保護法）改正動向**
- 2025年審議中・**2027年施行見込み**
- 音声データが「生体データ」として特別カテゴリに分類される可能性あり
- 今から対応設計しておくことを推奨

---

## 5. ローカルデプロイ可能なOSSモデル比較

| モデル | 日本語精度(CER) | 速度 | 最小GPU | ライセンス | 特徴 |
|--------|:-------------:|:----:|:------:|:--------:|------|
| **Whisper large-v3** | 8.5% | 標準 | RTX 3060(12GB) | MIT | 精度最高水準、多言語 |
| **Whisper large-v3-Turbo** | 8.8% | 5.4倍速 | RTX 3060(6GB) | MIT | 精度ほぼ同等・大幅高速化 |
| **faster-whisper (INT8量子化)** | 同等 | 4倍速 | RTX 3060 | MIT | VRAM削減・実運用向け最適解 |
| **kotoba-whisper v2.2** | 9.2% | 6.3倍速 | RTX 3060(8GB) | Apache 2.0 | 日本語特化・話者分離統合。専門用語は要評価 |
| **ReazonSpeech v2** | 高（詳細非公開） | 低速 | — | Apache 2.0 | 日本語720万件学習 |

**実運用の推奨**: `faster-whisper large-v3 INT8` が精度・速度・VRAM効率のバランス最良

### ローカル運用コスト目安（月500時間処理の場合）

| 選択肢 | 月額コスト | 初期費用 |
|-------|:--------:|:-------:|
| OpenAI Whisper API | ~$1,800/月 | なし |
| ローカル（RTX 4090購入） | 電気代+保守のみ | ~$2,000 |
| GPUクラウドインスタンス借用 | ~$200〜250/月 | なし |

→ **月100時間超でローカルGPUがTCO優位になる**

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
- **既存コードのエンドポイントURLを変えるだけで移行できる**

```python
from openai import OpenAI

# base_url をローカルに向けるだけ
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
| **Modal.com** | Pythonコードだけでデプロイ、オートスケール | $0.0001〜/リクエスト | ★ |
| **Replicate** | GUIでデプロイ、APIキーだけで呼べる | $0.0023/分 | ★（最簡単） |
| **Hugging Face Inference Endpoints** | GUIでモデル選んでデプロイ | $0.006〜/時間 | ★ |

### ③ 大手クラウド（VPC内閉じた処理が可能）

| クラウド | サービス | 特徴 |
|---------|---------|------|
| **AWS** | SageMaker + JumpStart | Whisper large-v3が公式サポート済み。VPC内で閉じた処理可 |
| **Azure** | Container Apps（Japan East） | Dockerイメージをそのままデプロイ可。APPI対応明確 |
| **GCP** | Cloud Run（GPU） | サーバーレスGPUで運用可 |

---

## 7. 医療・個人情報用途の選択フロー

```
データを院外に出せない？
├── YES（医療カルテ・要配慮個人情報等）
│   ├── 自社サーバーあり
│   │   → Speaches or whisper-asr-webservice をDockerデプロイ
│   ├── クラウド内で閉じたい
│   │   → AWS SageMaker in VPC / Azure Container Apps (Japan East)
│   └── 国産サポート・SLAが必要
│       → AmiVoice iNote / mocoVoice医療モデル（オンプレ専用）
│
└── NO（個人情報なし・教育/一般用途）
    ├── 手軽に試したい → Replicate or Hugging Face Endpoints
    ├── コスト最安    → RunPod or Modal（Serverless）
    ├── 大量バッチ   → AWS SageMaker 非同期エンドポイント
    └── 汎用バランス → OpenAI Whisper API（whisper-1）← 大抵これでOK
```

---

## 8. 国産・医療特化商用サービス（参考）

| サービス | 形態 | 日本語特化 | 医療対応 | 特徴 |
|---------|:----:|:--------:|:-------:|------|
| **AmiVoice iNote** | 院内オンプレ設置型 | ◎ 診療科別辞書 | ◎ | 月額3,300円〜 |
| **AmiVoice API Private** | 専用クラウド/オンプレ | ◎ | ◎ | 金融・医療向け。ISMS取得 |
| **mocoVoice医療モデル** | オンプレ専用 | ◎ 医療用語10万語 | ◎ | 2025年3月リリース。IT補助金対象 |

---

## 参考リンク

- [Soniox STT Benchmarks 2025](https://soniox.com/benchmarks)
- [VocaFuse STT API比較 2025](https://vocafuse.com/blog/best-speech-to-text-api-comparison-2025/)
- [Zenn：2025年日本語文字起こしモデル比較](https://zenn.dev/hongbod/articles/def04f586cf168)
- [GitHub - speaches-ai/speaches](https://github.com/speaches-ai/speaches)
- [GitHub - ahmetoner/whisper-asr-webservice](https://github.com/ahmetoner/whisper-asr-webservice)
- [AWS: Host Whisper on SageMaker](https://aws.amazon.com/blogs/machine-learning/host-the-whisper-model-on-amazon-sagemaker-exploring-inference-options/)
- [kotoba-whisper-v2.2 on Hugging Face](https://huggingface.co/kotoba-tech/kotoba-whisper-v2.2)
- [厚労省 医療情報システム安全管理ガイドライン第6.0版](https://www.mhlw.go.jp/stf/shingi/0000516275_00006.html)
- [Red Hat: Private transcription with Whisper（2026/03）](https://developers.redhat.com/articles/2026/03/06/private-transcription-whisper-red-hat-ai)
