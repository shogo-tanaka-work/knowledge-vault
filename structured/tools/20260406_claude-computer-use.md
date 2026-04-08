# Claude Computer Use Docker環境構築 検証ログ

> ステータス: 完了
> 作成日: 2026/04/06
> 最終更新: 2026/04/06
> ファイルパス: /Volumes/PortableSSD/Documents/knowledge-vault/structured/tools/20260406_claude-computer-use.md

---

## 検証概要

- **ツール/サービス名**: Claude Computer Use（Anthropic API beta機能）
- **検証対象**: Docker + noVNC環境でComputer Useエージェントを動作させ、Firefox GUIブラウザを自動操作する仕組みの構築
- **バージョン/リリース日**: API beta flag `computer-use-2025-01-24`、モデル claude-sonnet-4-20250514
- **検証期間**: 2026/04/06（1日で完結）
- **検証ステータス**: 完了

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- Anthropic Computer Use APIの実用性を検証し、業務自動化PoCの基盤環境を構築する
- GUIブラウザ（Firefox）を含む完全なデスクトップ環境をDocker内で動作させ、noVNC経由で操作を可視化する

### 解決したい課題
- Computer Useの「スクリーンショット→分析→操作」ループが実際にどの程度の精度で動くか確認
- Docker環境でのFirefox実行におけるARM64（Apple Silicon）固有の問題を解決
- macOS前提のコードベースをLinux Docker環境に移植

---

## 2. 技術構成

| コンポーネント | 技術 |
|---|---|
| コンテナ | Ubuntu 24.04 (Docker) |
| 仮想ディスプレイ | Xvfb |
| デスクトップ | XFCE4 |
| VNCサーバー | x11vnc |
| Webアクセス | noVNC (websockify) |
| ブラウザ | Firefox 149.0 (Mozilla公式バイナリ) |
| AI API | Anthropic Computer Use beta |
| Python | pyautogui, Pillow, anthropic SDK |

---

## 3. 遭遇した問題と解決策

### 3.1 ModuleNotFoundError: No module named 'computer_use'

- **原因**: `PYTHONPATH=/app` だがパッケージは `/app/src/computer_use/` に配置
- **解決**: Dockerfile で `ENV PYTHONPATH=/app/src` に変更

### 3.2 Ubuntu 24.04でFirefoxが起動しない

- **原因**: Ubuntu 24.04の`firefox`パッケージはsnap版への移行パッケージ。Dockerコンテナ内ではsnapdが動作しないため実体がない
- **試したこと**:
  1. Mozilla Team PPA (`ppa:mozillateam/ppa`) → ARM64でダウンロードが極端に遅く断念
  2. Mozilla公式バイナリ直接ダウンロード → **成功**
- **解決**: Dockerfileで以下の方式を採用
  ```dockerfile
  RUN ARCH=$(uname -m) && \
      if [ "$ARCH" = "aarch64" ]; then ARCH="linux64-aarch64"; else ARCH="linux64"; fi && \
      wget -q "https://download.mozilla.org/?product=firefox-latest-ssl&os=${ARCH}&lang=ja" \
        -O /tmp/firefox.tar.xz && \
      tar -xf /tmp/firefox.tar.xz -C /opt/ && \
      ln -sf /opt/firefox/firefox /usr/local/bin/firefox
  ```
- **追加依存**: `libdbus-glib-1-2`, `libgtk-3-0`, `libasound2t64`, `xz-utils` が必要

### 3.3 pyautogui の Xauthority / tkinter エラー

- **原因**: `.Xauthority` ファイルが存在しない + `python3-tk` 未インストール
- **解決**: Dockerfileに `python3-tk`, `python3-dev` を追加、entrypoint.shで `touch ~/.Xauthority`

### 3.4 macOS前提のコードをLinux環境に移植

元コードは完全にmacOS前提（screencapture, osascript, pbcopy等）。以下4ファイルを修正:

| ファイル | 変更内容 |
|---|---|
| `agent.py` | システムプロンプトをLinux/Firefox/XFCE用に全面書き換え（ctrl系ショートカット、firefox起動方法等） |
| `config.py` | スクリーン検出を `osascript` → `xdpyinfo` + 環境変数フォールバックに変更 |
| `computer.py` | スクリーンショット: `screencapture` → `scrot`、クリップボード: `pbcopy` → `xclip`、キーマッピング: cmd → ctrl |
| `Dockerfile` | Firefox PPA → 公式バイナリ、xclip/x11-utils等追加 |

---

## 4. 検証結果

### 動作確認

タスク `"Firefoxでgoogle.comを開いてClaude AIを検索して"` を実行:

- **結果**: 成功（15イテレーション、30メッセージ交換で完了）
- **エージェントの動作フロー**:
  1. スクリーンショットでデスクトップ確認
  2. `firefox &` でブラウザ起動
  3. アドレスバーにgoogle.comを入力
  4. 検索ボックスに「Claude AI」を入力
  5. 検索結果を確認・スクロール
- **noVNC**: http://localhost:6080 でFirefoxの操作がリアルタイムに可視化された

### スケーリング

- Xvfbの解像度とClaudeの論理解像度が一致（1280x832）するためスケール1.0
- 座標変換の誤差なし

---

## 5. 学んだこと・知見

### Docker内でのGUIブラウザ運用
- Ubuntu 24.04以降、多くのパッケージがsnapに移行しておりDockerとの相性が悪い
- Mozilla公式バイナリの直接ダウンロードが最も確実
- ARM64（Apple Silicon）環境では `linux64-aarch64` を指定する必要がある

### Computer Useエージェントの特性
- システムプロンプトが非常に重要。環境に合わない指示（macOSコマンド等）があるとエージェントが迷走する
- 「使えるブラウザはFirefoxのみ」「macOSコマンドは使うな」等の明示的な制約が効果的
- エージェントは失敗するとChromiumインストールやテキストブラウザに逃げがち → プロンプトで封じる

### PoCに適するタスク（公式推奨条件）
- バッチ処理 / 再試行可能 / 低リスクデータ / 時間圧力なし

---

## 6. 次のステップ

業務目線のPoC候補を `POC_IDEAS.md` として整理済み。優先度の高い候補:

1. レガシーシステムへのデータ入力自動化
2. 行政ポータルの操作自動化
3. 競合調査・市場情報収集

Git公開後にIssueとして起票予定。
