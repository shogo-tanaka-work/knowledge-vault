---
title: Claude Code + Expo で iOS アプリを実機導入するまでに踏んだ地雷を全部書く
status: draft
created: 2026-06-01
updated: 2026-06-01
type: tech-tutorial
related:
  - structured/projects/20260601_claude-code-ios-app.md
medium: tech-blog
target_cta: GitHub（workout-habit-app リポジトリ）
target_platforms:
  - Zenn
  - Qiita
---

# Claude Code + Expo で iOS アプリを実機導入するまでに踏んだ地雷を全部書く

## TL;DR

- Claude Code に任せて Expo（React Native）製の iOS アプリを作り、シミュレータから実機（無料 Apple ID・ローカルビルド）への導入まで通した
- 詰まったのはコードではなく環境側。特に次の4つが地雷だった
  - 日本語を含むパスで `pod install` が `bad component` で失敗する（RN 0.85 の prebuilt artifacts が原因）
  - `npm run ios:dev --device` は `--` がないと引数が expo に渡らずシミュレータに入る
  - iOS 16+ は実機開発に端末側「デベロッパモード」が必須
  - ターミナルからの codesign が `errSecInternalComponent` で落ちる（キーチェーンの鍵アクセス）
- 単体で持ち歩くには Metro 依存の dev build ではなく、JS を内蔵する Release ビルドが要る
- 無料 Apple ID はアプリが7日で失効する

環境は macOS（Apple Silicon）/ Xcode 26.5 / Node 22 / Expo SDK 56 / React Native 0.85。

## 課題設定

やりたかったのは、AIコーディングだけでネイティブ iOS アプリを「自分の iPhone で動く」ところまで届かせることだった。実装そのものは Claude Code がかなりの速度で進める。問題は、その前後にあるネイティブ特有の工程（CocoaPods、署名、実機の設定）で、ここはエラーメッセージの読解と環境知識が要る。本稿はその実録で、同じ構成で詰まる人の時間を節約することを狙う。

題材は筋トレ記録アプリ。記録のCRUDとローカル保存（SQLite）が中心の小さな MVP で、構成の単純さゆえに「周辺の地雷」だけがくっきり残った。

## 全体アーキテクチャ

```
[ Claude Code ] --- 実装/ビルド実行/デバッグ
       |
       v
[ Expo (React Native) アプリ ]
   - UI: React Native (単一 App.tsx)
   - 永続化: expo-sqlite (端末内 SQLite)
   - 音: expo-audio (タイマー終了音)
   - 入力UI: @react-native-picker/picker (ホイール)
       |
   expo run:ios（prebuild → pod install → xcodebuild）
       |
       +--- Debug ビルド（dev client）→ Metro から JS を取得
       +--- Release ビルド → JS を内蔵（単体動作）
       |
       v
[ iPhone 実機 ] 無料 Apple ID + ローカル署名
```

| レイヤ | 採用 | 補足 |
|---|---|---|
| フレームワーク | Expo SDK 56 / React Native 0.85 | `expo run:ios` でネイティブビルド |
| 言語 | TypeScript | `tsc --noEmit` で型チェック |
| 永続化 | expo-sqlite | オフライン前提のローカル保存 |
| ネイティブ依存解決 | CocoaPods 1.16.2 | Expo SDK 56 が前提 |
| ファイル監視 | Watchman | RN 推奨 |
| ビルド/署名 | Xcode 26.5 | 無料 Apple ID（Personal Team） |

## 環境構築：CocoaPods はまだ必要

`expo run:ios` は内部で `pod install` を呼ぶため、CocoaPods が要る。Homebrew で入れた。

```bash
brew install cocoapods
brew install watchman   # 推奨
pod --version           # 1.16.2
```

CocoaPods は2026年にメンテナンスモード入りがアナウンスされており、React Native は Swift Package Manager (SPM) 対応を進めている。ただし現時点で SPM 対応は実験的で、Expo SDK 56 の prebuild フローからは使えない。`expo run:ios` が CocoaPods 前提で固定されているため、いまは CocoaPods を入れるのが唯一の現実解になる。これはアプリ開発者側で差し替える話ではなく、Expo/RN のツールチェーンが対応した時点で自動的に不要になる将来課題と捉えるのがよい。

ライセンスとパスは、Xcode を入れて一度起動すれば概ね整う。`xcode-select -p` が `/Applications/Xcode.app/Contents/Developer` を指していれば Command Line Tools ではなく Xcode 本体が選択されている。

## 地雷1：日本語パスで `pod install` が落ちる

最初のビルドで `pod install` がこのエラーで止まった。

```
[ReactNativeCore] Failed to download release tarball:
  bad component(expected absolute path component):
  /Users/.../筋トレ習慣化アプリ/20_開発/.../reactnative-core-0.85.3-debug.tar.gz
[!] The `React-Core-prebuilt` pod failed to validate due to 1 error:
    - ERROR | attributes: Missing required attribute `source`.
```

原因は、React Native 0.85 から既定になった prebuilt artifacts の仕組みにある。ビルド済みバイナリを Maven から取得して高速化する機能で、ダウンロード先のローカル絶対パスを `file://` URI に変換する。このとき、パスに日本語（マルチバイト文字）が含まれると Ruby 側の URI 処理が `bad component` で失敗し、結果として podspec の `source` 属性が設定されず検証エラーになる。

`node_modules/react-native/scripts/cocoapods/rncore.rb` を読むと、ソースビルドが本来の既定（`@@build_from_source = true`）で、`RCT_USE_PREBUILT_RNCORE == "1"` のときだけ prebuilt を使う。生成された `ios/Podfile` を見ると Expo が次のように prebuilt を有効化していた。

```ruby
ENV['RCT_USE_RN_DEP'] ||= podfile_properties['ios.buildReactNativeFromSource'] == 'true' ? '0' : '1'
ENV['RCT_USE_PREBUILT_RNCORE'] ||= podfile_properties['ios.buildReactNativeFromSource'] == 'true' ? '0' : '1'
```

### 対処：パスを ASCII 化する

回避策として `ios.buildReactNativeFromSource: true`（ソースビルド強制）もあるが、初回ビルドが大幅に遅くなるうえ、Apple のツールチェーン（Xcode の DerivedData、署名、Hermes）はそもそもマルチバイトパスに弱く、別の箇所で再発しやすい。根治はパスの ASCII 化が確実だ。

プロジェクト配下のフォルダ名を英語へリネームし、ビルドパスから日本語を一掃した。

```
（例）
10_プロジェクト        → 10_projects
筋トレ習慣化アプリ      → workout-habit
20_開発               → 20_dev
```

リネーム後は、旧パスが焼き込まれた `ios/` と `.expo/` を消してから再生成する。

```bash
rm -rf ios .expo
npm run ios:dev   # prebuild からやり直し
```

これで prebuilt tarball の `source` が正しく設定され、`pod install` が通り、シミュレータで起動した。

> 教訓：iOS/RN のネイティブビルドを行うプロジェクトは、最初から ASCII のみのパスに置く。日本語ディレクトリ運用をしている場合でも、コード本体だけは英語パスに分離するのが安全。

## 地雷2：`--device` が npm に食われる

実機ビルドのつもりで次を実行したが、シミュレータに入ってしまった。

```bash
npm run ios:dev --device   # ❌ --device が npm のフラグとして消費される
```

ログを見ると `Debug-iphonesimulator` をビルドしていた。npm script に引数を渡すには `--` の区切りが要る。

```bash
npm run ios:dev -- --device <あなたのデバイスのUDID>
# または
npx expo run:ios --device <あなたのデバイスのUDID>
```

接続中デバイスの UDID は次で確認できる。

```bash
xcrun xctrace list devices    # == Devices == セクションに UDID が出る
```

## 署名の準備：無料 Apple ID で十分

実機ビルドには署名が要る。最初は署名 ID が0件だった。

```bash
security find-identity -v -p codesigning   # 0 valid identities found
```

無料 Apple ID で最初の一度だけ Xcode 側で設定する。

1. Xcode を起動して `ios/<App>.xcworkspace` を開く（`open ios/*.xcworkspace`）
2. Xcode > Settings > Accounts で Apple ID を追加（Personal Team が作られる）
3. ターゲットの Signing & Capabilities で「Automatically manage signing」を有効化し、Personal Team を選択

これで開発用証明書とプロビジョニングプロファイルが作られ、`project.pbxproj` に `DEVELOPMENT_TEAM` が書き込まれる。

```bash
security find-identity -v -p codesigning
#   1) XXXXXXXX "Apple Development: your-apple-id@example.com (XXXXXXXXXX)"
grep -E "DEVELOPMENT_TEAM" ios/*.xcodeproj/project.pbxproj
#   DEVELOPMENT_TEAM = XXXXXXXXXX;
```

## 地雷3：Developer Mode が無効

署名が整ってから実機ビルドすると、今度はこれで止まった。

```
error: Developer Mode disabled
To use <device> for development, enable Developer Mode in
Settings → Privacy & Security.
```

iOS 16 以降は、実機に開発ビルドを入れるのに端末側の「デベロッパモード」が必須になっている。一度ビルドを試行すると iPhone の設定にトグルが出現する。

iPhone 操作：設定 → プライバシーとセキュリティ → デベロッパモード → オン → 再起動 → 起動後に確認ダイアログで有効化。`xcrun devicectl list devices` の表示が `no DDI` から `connected` に変われば準備完了の目安になる。

## 地雷4：`errSecInternalComponent` で codesign が落ちる

実機向けのビルド自体は成功したのに、最後の署名フェーズで落ちた。

```
WorkoutHabit.debug.dylib: errSecInternalComponent
❌  Script '[CP] Embed Pods Frameworks' failed
xcodebuild exited with error code 65
```

これは典型的なキーチェーンの署名鍵アクセス問題だ。ターミナル（非GUIで起動したプロセス）から `codesign` が鍵を使おうとすると、キーチェーンの許可ダイアログを出せずに失敗する。

### 対処A（推奨・一回だけ）：Xcode から Run する

Xcode でデバイスを選び ▶ Run すると、GUI 文脈で codesign が走り、「codesign が鍵を使用しようとしています」ダイアログが出る。ここで「常に許可」（要 Mac ログインパスワード）を押すと鍵の ACL が更新され、以降はターミナルからの署名も通る。

### 対処B（CLI 派）：partition list を更新する

```bash
security set-key-partition-list \
  -S apple-tool:,apple:,codesign: -s \
  -k "<Macログインパスワード>" \
  ~/Library/Keychains/login.keychain-db
```

`<Macログインパスワード>` はログインキーチェーンのパスワードで、初期設定では macOS のログインパスワードと同じだ。コマンドにパスワードが残るので、自分の手元で実行することを勧める。まずは対処A（Xcode の Run + 常に許可）が簡単で確実だった。

## 地雷5：「信頼されていないデベロッパ」

初回起動時、iPhone 側で信頼を求められる。

iPhone 操作：設定 → 一般 → VPNとデバイス管理 →「デベロッパAPP」→ 自分の Apple ID →「信頼」。
無料 Apple ID の証明書は Apple のサーバーで検証するため、この操作には端末のネット接続が必須になる。オフラインだと検証で止まる。

## dev build と Release build の違い（重要）

ここを理解していないと、実機に入れても「Mac の前でしか動かない」状態になる。

| | 開発ビルド（Debug / dev client） | Release ビルド |
|---|---|---|
| JS の供給 | Mac の Metro が必要（同一Wi-Fi） | アプリに内蔵（単体・オフライン動作） |
| 持ち歩き利用 | 不可 | 可 |
| コマンド | `npx expo run:ios --device <UDID>` | `npx expo run:ios --device <UDID> --configuration Release` |
| 用途 | 開発中の高速イテレーション | 実際に使う・配る |

dev client はアプリ起動時に Metro から JS を取得する。ジムなど Mac から離れた場所で使うなら、JS をバンドルに内蔵する Release ビルドが要る。

```bash
# 単体で動く版を実機へ
npx expo run:ios --device <あなたのデバイスのUDID> --configuration Release
```

`Build Succeeded` の後、`Release-iphoneos/<App>.app` がインストールされれば、Mac も Metro も Wi-Fi もなしで起動する。データは端末内 SQLite に保存されるため、オフラインでも記録できる。

## 計測・結果

- `npm run typecheck`（`tsc --noEmit`）: 成功
- Xcode: `Build Succeeded`（Debug-iphoneos → 後に Release-iphoneos）
- 実機（iPhone / iOS 26.5）に Release 版をインストールし、単体起動を確認
- 体感の所要：企画レビューから実機導入まで一日。うちコードより環境の地雷解決に時間を取られた

ハマりポイントを一覧で残す。

| # | 症状 | 原因 | 対処 |
|---|---|---|---|
| 1 | `pod install` が `bad component` | 日本語パスを prebuilt が URI 化できない | フォルダ名を ASCII 化し `ios/`・`.expo` 再生成 |
| 2 | シミュレータに入る | `npm run ios:dev --device` の `--` 欠落 | `npm run ios:dev -- --device <UDID>` |
| 3 | `Developer Mode disabled` | iOS 16+ の実機開発要件 | 端末でデベロッパモードを有効化＋再起動 |
| 4 | `errSecInternalComponent` | 非GUIからの codesign が鍵にアクセス不可 | Xcode で Run し「常に許可」/ `set-key-partition-list` |
| 5 | 「信頼されていないデベロッパ」 | 無料証明書の未信頼 | 設定→VPNとデバイス管理で信頼（要ネット接続） |
| 6 | 数日でアプリが失効 | 無料 Apple ID は7日で期限切れ | 同コマンドで再インストール |

## 横展開

この環境構築・署名・実機導入の型ができると、別のモバイル PoC にもそのまま再利用できる。受託や社内導入の前に「動く検証機」を手元で組み、要件や技術選定の妥当性を実物で確かめてから投資判断に進める。常用やβ配布（期限延長・TestFlight）まで広げるなら、Apple Developer Program（年99ドル）と EAS Build に移行する。

## まとめ

Claude Code に任せれば、Expo + RN の iOS アプリ実装は素直に進む。一方で、実機到達のボトルネックはネイティブ環境側に集中する。本稿の6つの地雷（日本語パス、`--device` の `--`、Developer Mode、キーチェーン署名、信頼設定、無料枠の失効）を先に潰しておけば、実装から実機導入までの距離はかなり短くなる。詰まったらエラーメッセージをそのまま AI に渡すのが結局いちばん速かった。

---

Zenn 用タグ: `ClaudeCode` `Expo` `ReactNative` `iOS` `CocoaPods`
Qiita 用タグ: `ClaudeCode` `Expo` `ReactNative` `Xcode` `コード署名`
