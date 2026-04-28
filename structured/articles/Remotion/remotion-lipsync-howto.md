---
title: "Remotionで口パク動画を作る：素材準備から実装まで"
status: draft
media: note
created: 2026-04-28
updated: 2026-04-28
source_project: ""
published_url: ""
---

# Remotionで口パク動画を作る：素材準備から実装まで

## 参考記事

- [Remotionで口パク動画を作る方法 | note（aiaicreate）](https://note.com/aiaicreate/n/ndd8eac6b2cc1?magazine_key=m1b26d058cab2)
- [EasyPNGTuberで表情差分を作る方法 | note（rotejin）](https://note.com/rotejin/n/n106abaaa3957)

---

## 全体フロー

```
[立ち絵1枚]
    ↓ EasyPNGTuber（記事2）
[表情差分4枚（2×2グリッド）]
    ↓
[Remotionプロジェクト]＋[音声ファイル]＋[FFmpeg]
    ↓ 口パク解析スクリプト
[mouth-cues.json]
    ↓ Composition.tsx
[口パク動画]
```

---

## PHASE 1: 表情差分画像の準備（EasyPNGTuber）

> 参考: https://note.com/rotejin/n/n106abaaa3957

### 必要なもの

- Python（uvで実行）
- EasyPNGTuber リポジトリ（GitHub）
- Google Nano Banana または Google AI Studio（表情差分のAI生成に使用）
- 元となるキャラクター立ち絵 1枚

### 手順

#### ステップ1: 立ち絵をグリッド化

```bash
uv run python grid_tiler.py
```

1. キャラ画像をドラッグ&ドロップ
2. 「タイリング画像を保存」で **2×2グリッド形式**に変換して保存

#### ステップ2: AI（Nano Banana）で表情差分を生成

グリッド画像を参考画像として添付し、以下の4パターンを1枚の2×2画像として生成するようプロンプトで指示する。

| 位置 | 内容 |
|:---:|:---|
| 左上 | 未使用（元画像のまま） |
| 右上 | 目開き |
| 左下 | 目閉じ・口閉じ |
| 右下 | 目閉じ・口開き |

> **Tips**: 差分の品質が微妙な場合は新規チャットで再生成する。ベース画像は「目と口が同じ状態」のものが推奨。慣れると約3〜5分で完成。

#### ステップ3: パーツ抽出・4パターン保存

```bash
uv run python parts_mixer.py
```

1. AI生成画像をドラッグ&ドロップ
2. 「分割&位置合わせ」ボタンをクリック
3. ベース画像を選択
4. ブラシで**目と口の領域をマスク**
5. 「4パターン一括保存」で出力

### 出力される4枚の画像

| ファイル | 表情 |
|:---|:---|
| `eye-open_mouth-close.png` | 目開・口閉 |
| `eye-open_mouth-open.png` | 目開・口開 |
| `eye-close_mouth-open.png` | 目閉・口開 |
| `eye-close_mouth-close.png` | 目閉・口閉 |

> ファイル名はプロジェクト側の命名規則に合わせて変更する。

---

## PHASE 2: Remotionで口パク動画を実装

> 参考: https://note.com/aiaicreate/n/ndd8eac6b2cc1

### 必要なもの

- Node.js / npm
- Remotion（`npm create video`等でプロジェクト作成）
- FFmpeg（音声解析に使用）
- 表情差分画像4枚（PHASE 1で作成）
- 音声ファイル（`public/audio/narration.wav`）

#### FFmpegのインストール（Windows/PowerShell）

```powershell
# winget経由
winget install FFmpeg
```

手動セットアップも可能（PATH設定が必要）。

### プロジェクト構成

```
project/
├── public/
│   └── audio/
│       └── narration.wav       ← 音声ファイルをここに配置
├── scripts/
│   └── generate-lipsync.mjs    ← 音声解析スクリプト
└── src/
    ├── lipsync/
    │   └── mouth-cues.json     ← 生成されるJSONデータ
    └── Composition.tsx         ← メインのコンポーネント
```

### 手順

#### ステップ1: 音声ファイルの準備

音声は `public/audio/narration.wav` に配置。  
Irodori-TTS 等のTTSツールで生成してWAV形式で書き出す。

#### ステップ2: 音声解析スクリプトの作成・実行

`scripts/generate-lipsync.mjs` を作成し実行する。  
スクリプトはFFmpegを使って音声を解析し、フレームごとの口開閉データをJSONで出力する。

**スクリプト仕様**

| パラメータ | 値 |
|:---|:---|
| FPS | 30 |
| サンプルレート | 16000 |
| 出力先 | `src/lipsync/mouth-cues.json` |

**実行**

```bash
node scripts/generate-lipsync.mjs
```

#### ステップ3: 生成されるJSONの確認

```json
{
  "fps": 30,
  "mouthByFrame": [0, 1, 1, 0, 1, 0, ...]
}
```

- `0` = 口閉じ
- `1` = 口開き

#### ステップ4: Composition.tsx の実装

フレーム番号に応じて `mouthByFrame` の値を参照し、対応する表情差分画像を切り替えることで口パクを実現する。

**基本的なロジック**

```tsx
import { useCurrentFrame } from 'remotion';
import mouthCues from './lipsync/mouth-cues.json';

// フレームに対応する口の状態を取得
const frame = useCurrentFrame();
const isMouthOpen = mouthCues.mouthByFrame[frame] === 1;

// 状態に応じて画像を切り替える
const mouthImage = isMouthOpen ? 'eye-open_mouth-open.png' : 'eye-open_mouth-close.png';
```

#### ステップ5: 動作確認

```bash
npm run dev
```

ブラウザでプレビューを確認する。解像度の調整が必要な場合はComposition設定で変更する。

---

## プロンプト活用（AIコーディング支援）

記事1では以下の3パターンのプロンプトを用意してAIにコード生成させることを推奨している。

| パターン | 用途 |
|:---|:---|
| 統合版 | スクリプト（.mjs）＋TSXを一括生成 |
| スクリプト単独版 | `generate-lipsync.mjs` のみ生成 |
| TSX単独版 | `Composition.tsx` のみ生成 |

各プロンプトにはファイルパス・fps・sampleRate・出力形式を明記して渡す。

---

## 注意点・Tips

- FFmpegは必須。PATH設定が通っていないと解析スクリプトが動かない
- 表情差分はベース画像の「目と口の状態」を統一しておくと差分品質が安定する
- 解像度調整はAIへの追加指示で対応可能
- 口パクの精度はFFmpegの音声解析精度に依存するため、クリアな音声ファイルを用意する

---

## 関連リソース

- [Remotion 公式ドキュメント](https://www.remotion.dev/docs)
- [FFmpeg 公式サイト](https://ffmpeg.org)
- [Irodori-TTS（音声生成）](https://irodori-tts.com)
- [imagy.app（画像分割ツール）](https://imagy.app)
