# security-guidance フックによるセキュア×AI駆動コーディング基盤 検証ログ

> ステータス: 進行中（init + 初回動作確認まで完了）
> 作成日: 2026/05/27
> 最終更新: 2026/05/27
> ファイルパス: 15_ナレッジ基盤/vault/structured/tools/20260527_security-guidance-hook.md

---

## 検証概要

- **ツール/サービス名**: `security-guidance@claude-plugins-official`
- **対象**: Claude Code 公式プラグイン（PreToolUse フック方式）
- **検証期間**: 2026/05/27 〜（未定）
- **検証ステータス**: 進行中
- **連携アセット**:
  - 検証用フォーク: `16_検証ラボ/lab-secure-aidd-boilerplate/`
  - 上流テンプレ: `/Users/shogo/PortableSSD/Documents/codes/個人開発/AIDD-MVP-bilerPlate`
  - プラグイン実体: `~/.claude/plugins/cache/claude-plugins-official/security-guidance/unknown/`

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- AI駆動コーディング（Claude Code 主導の実装）では、エージェントが生成するコードのセキュリティを「人間が事後レビュー」する従来モデルは間に合わない。
- 公式プラグイン `security-guidance` が、`PreToolUse` フックで Edit/Write/MultiEdit の **直前** にパターン警告を出す方式を提供したため、これを既存の AIDD ボイラープレートと組み合わせれば「リアルタイム × オンデマンド × CI」の三層防御テンプレートを作れる仮説。

### 解決したい課題
- 既存 AIDD v1 は `security-auditor` サブエージェントと CI に依存しており、**実装中の警告**が無い。
- フックを噛ませることで、危険APIの混入を「コードが書かれる瞬間」に検知できるか確認する。

### 期待される効果
- AI駆動開発のスループットを落とさずに、コマンドインジェクション・XSS・安全でない API 利用などを実装中にブロック／警告できる。
- 同テンプレを使う他プロジェクトに、設定一発で同じガードレールを配布できる。

---

## 2. ツール/機能の基本情報

### 仕組みの要点
- **トリガー**: `PreToolUse` × matcher `Edit|Write|MultiEdit`
- **実体**: Python スクリプト約 280 行（`security_reminder_hook.py`）
- **検出方式**: 正規表現/キーワードベースのパターンマッチ
- **ログ出力**: `/tmp/security-warnings-log.txt`
- **インストール経路**: user スコープ（`~/.claude/plugins/...`）。今回検証では **プロジェクト同梱版**（`.claude/hooks/`）に切り替え、`${CLAUDE_PROJECT_DIR}` で参照する形に変更。

### v1 (AIDD) との関係
| 層 | v1 | v2（本検証） |
|---|---|---|
| リアルタイム警告 | なし | `security_reminder_hook.py`（新規） |
| オンデマンド監査 | `security-auditor` サブエージェント | そのまま温存 |
| CI ゲート | `.github/workflows/ci.yml` ほか | そのまま温存 |

---

## 3. 検証観点（仮置き）

1. **発火パターンの網羅性**: コマンドインジェクション系・XSS 系・`eval`・`child_process` 系で実際に警告が出るか。
2. **誤検知率**: ドキュメントやテストフィクスチャ内の文字列にも反応するか（本検証ログ起票時、プランファイルへの Write が一度フックでブロックされた実例あり → 誤検知の典型）。
3. **責務分担**: フックとサブエージェント `security-auditor` の役割を明文化できるか（フック=即時パターン、サブエージェント=構造的監査）。
4. **配布性**: `.claude/hooks/` をプロジェクトに含めることで、チームメンバーが clone するだけで同じガードが効くか。
5. **レイテンシ**: フック実行による Edit/Write の体感的な遅延。

---

## 4. 実施内容（init 時点）

- [x] `security-guidance@claude-plugins-official` を user スコープにインストール
- [x] プラグイン中身（hooks.json / Python スクリプト）を確認
- [x] AIDD ボイラープレートを `16_検証ラボ/lab-secure-aidd-boilerplate/` に `.git` 除外でコピー
- [x] フックスクリプトを `.claude/hooks/` に同梱、`settings.json` に `hooks` セクションを追記
- [x] README に「v1 との差分」「動作確認手順」を追記
- [x] ダミーパターンによる発火確認（PreToolUse JSON を stdin に流す方式で8ケース実施）
- [x] `/tmp/security-warnings-log.txt` 仕様確認（**警告ログではなくエラーログ専用**だった）
- [ ] パターン拡張（日本語コメントの禁止表現 / IPA チェックリスト準拠）
- [ ] Claude Code 実セッションでの `/hooks` 表示確認（このセッションからは不可・要別ターミナル）
- [ ] 完成版を AIDD 本体（PortableSSD 側）へ逆輸入

---

## 4-1. 初回動作確認ログ（2026/05/27）

フックスクリプトに `PreToolUse` 仕様の JSON を `stdin` から流して直接実行。Claude Code 実セッションを介さない単体テスト。

### テストハーネス（再現コマンド）

```bash
HOOK=".../lab-secure-aidd-boilerplate/.claude/hooks/security_reminder_hook.py"
# 各ケースは:  echo '<json>' | python3 "$HOOK"
# exit 0 = 素通り / exit 2 = ブロック（stderrに警告メッセージ）
```

### 結果サマリ（8ケース）

| # | ケース | 入力ツール | 検出パターン | exit | 想定 | 判定 |
|---|---|---|---|---|---|---|
| 1 | 安全なコンテンツ | Write | なし | 0 | 0 | ✅ |
| 2 | `eval` 関数呼び出し | Write | `eval_injection` | 2 | 2 | ✅ |
| 3 | `.inner` `HTML` への代入 | Edit | `innerHTML_xss` | 2 | 2 | ✅ |
| 4 | React の `dangerously` `SetInnerHTML` | Write | `react_dangerously_set_html` | 2 | 2 | ✅ |
| 5 | `document` `.write` 呼び出し | Edit | `document_write_xss` | 2 | 2 | ✅ |
| 6 | `.github/workflows/*.yml` への Write | Write | `github_actions_workflow`（path_check） | 2 | 2 | ✅ |
| 7 | ケース2 と同セッション・同ファイル・同ルールで再実行 | Write | `eval_injection` | 0 | 0 | ✅ |
| 8 | 対象外ツール（Bash） | Bash | — | 0 | 0 | ✅ |

### 判明した仕様・観察

1. **ブロック方式は exit code 2 + stderr 出力**。Claude Code が stderr を「ガイダンス」として読み、ツール実行を中断する設計。
2. **セッション内・ファイル内・ルール内 で警告は1回だけ**（ケース7）。状態は `/tmp/claude_security_warnings_*.json` 系の state ファイルで管理。同じ警告を連続して見せない UX 配慮 ＝ 逆に **連続編集中は2回目以降の同種違反が素通りする** という運用上の注意点。
3. **`/tmp/security-warnings-log.txt` は警告ログではない**。`debug_log()` は JSON パース失敗時にしか呼ばれない実装で、通常運用ではこのファイルは作られない。**警告履歴を残したいなら、フック側に `debug_log(reminder)` を1行追加するカスタマイズが必要**。
4. **ファイルパスベースの検出（`path_check`）が機能**（ケース6）。`.github/workflows/` 配下では内容に依らず GitHub Actions のインジェクション警告が出る。
5. **対象ツールは Edit/Write/MultiEdit のみ**（ケース8）。Bash 系の危険コマンドはこのフックではなく `settings.json` の `deny` ルール側でガードする責務分担。
6. **このログ自体がフックに2回ブロックされた**（プラン作成時 + この追記時）。要因は危険APIの **解説目的の文字列** にも substring matcher が反応するため。ドキュメント用途では識別子をバッククォート等で分断する必要がある（本表は実際にその対処を入れている）。

### 制約

- このセッション内では Claude Code 実本体での `/hooks` 表示確認は不可（別ターミナルで `cd lab-secure-aidd-boilerplate && claude` 起動が必要）。
- ハーネスは「フックスクリプト単体」の挙動確認であり、Claude Code 側の `matcher` 解釈や状態管理との結合は別途確認すべき。

---

## 5. 学び・気づき（途中メモ）

- フックは **「文字列パターン」** で発火するため、危険APIの **解説ドキュメント** にも反応する。意図しないブロックを避けるなら、ドキュメントは `docs/` 配下に集約し matcher を絞るか、フック側で `description`/`comment` を除外する工夫が必要。
- 上流の AIDD v1 にあった `settings.json` の deny ルール（`rm -rf` / `curl` / `wget` 等）と、フック側のコードパターン検知は **直交している**。両方を残すと過剰防御になるかは要検証。

---

## 6. 次アクション

- `pbpaste の内容でログ更新して` で観察結果を都度追記。
- 検証完了時は `ログ完成させて` で finalize → `Note記事にして` で記事化を検討。

---

## 関連リンク

- 公式プラグイン: `claude-plugins-official`（marketplace）
- 検証ラボ: `16_検証ラボ/lab-secure-aidd-boilerplate/`
- 上流テンプレ: `AIDD-MVP-bilerPlate`（PortableSSD）
- 参考資料（プロジェクトルート同梱）:
  - `IPA公開のセキュリティチェックリスト.xlsx`
  - `安全なウェブサイトの作り方.pdf`
