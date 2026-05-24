---
title: Claude CodeとBrowser Use CLIでGoogleトレンド「探す」タブからYouTube検索トレンドを毎週取得する
status: draft
created: 2026-05-24
updated: 2026-05-24
type: tech-tutorial
related:
  - structured/tools/20260514_sns-research-automation.md
medium: tech-blog
target_cta: GitHub（browser-use-googletrends スキルリポジトリ）
target_platforms:
  - Zenn
  - Qiita
---

# Claude CodeとBrowser Use CLIでGoogleトレンド「探す」タブからYouTube検索トレンドを毎週取得する

<!-- 画像案①（アイキャッチ）: Claude Code → Browser Use CLI → Google トレンド explore タブ の流れを示す横長構成図 -->

## TL;DR

- Googleトレンドの`/trends/explore`を`gprop=youtube`で叩くと、YouTube検索ベースのキーワードが地域・期間指定で取れる
- `videos.list?chart=mostPopular`（YouTube Data API v3）は再生数ベース。検索意図のトレンドとは別物
- Browser Use CLIの`open` → `sleep 12` → `eval "document.body.innerText"`が安定運用の最小単位
- JS描画待ち12秒、`get text`は空、403/Captchaは実Chromeプロファイル切替、という地雷を全部書く
- Claude Codeスキル（SKILL.md + reference.md）化して、毎週月曜朝に自然言語で叩けるようにした

対象読者：SNSリサーチを自動化したい運用代行・マーケター、LLMエージェントでブラウザ自動化を組む開発者。

---

## 1. 課題設定：YouTube Data APIだけでは足りない

YouTube Data API v3の`videos.list?chart=mostPopular`で取れるのは再生数ベースの人気動画。SNSリサーチで欲しいのは「いま検索されているキーワード」で、これは別物。視聴者の入力ワードが分かればショート動画の企画タイトルに直結する。

Googleトレンドには`gprop=youtube`でYouTube検索クエリに絞るモードがある。これは公式API化されておらず、ブラウザ経由で取るしかない。そこでBrowser Use CLIを使う。

---

## 2. 全体アーキテクチャ

```
Claude Code（Sonnet 4.6）
  └─ スキル発動（"YouTubeトレンドを取得して"）
      └─ Browser Use CLI
          ├─ open <Google Trends explore URL>
          ├─ sleep 12（JS描画待ち）
          ├─ get title（疎通確認）
          ├─ eval "document.body.innerText"（本体取得）
          ├─ scroll down ×3〜5（50件未満時）
          └─ close
      └─ 取得テキスト → Claude が整形 → Markdownで出力
```

| ファイル | 役割 |
|---|---|
| `~/.claude/skills/browser-use-googletrends/SKILL.md` | トリガー定義、基本フロー、出力フォーマット |
| `~/.claude/skills/browser-use-googletrends/reference.md` | コマンドリファレンス、URLパラメータ仕様、アンチボット対策 |

Pythonスクリプトは書いていない。`browser-use`を直接Claudeから叩き、整形はClaude側に任せる。理由は後述。

---

## 3. 技術スタック

| 要素 | 採用 | 補足 |
|---|---|---|
| データソース | Google トレンド `/trends/explore` | 認証不要、公開情報 |
| ブラウザ自動化 | Browser Use CLI | `open` / `eval` / `scroll` / `close` |
| 描画エンジン | Playwright（Chromium） | `playwright install chromium` |
| オーケストレーション | Claude Code | スキル経由で発動 |
| 配布形式 | Claude Code Skill（`SKILL.md` + `reference.md`） | チーム配布 |

`pip install browser-use[cli]`で入る。Python 3.11以上。

---

## 4. Googleトレンド「探す」タブとは

`https://trends.google.co.jp/trends/explore`が「探す」（Explore）タブ。`/trending`の急上昇タブとは別で、検索クエリのボリューム推移と関連キーワードを返す。`gprop`でデータソースを切り替え、`youtube`指定でYouTube検索に絞れる。

### URLパラメータ仕様

| パラメータ | 値の例 | 説明 |
|---|---|---|
| `date` | `today 1-m` | 過去1ヶ月 |
| `date` | `now 7-d` | 過去7日間 |
| `date` | `today 12-m` | 過去12ヶ月 |
| `geo` | `JP` | 日本 |
| `geo` | `US` | アメリカ |
| `gprop` | `youtube` | YouTube検索フィルター（未指定はWeb検索） |
| `gprop` | `images` | Google画像検索 |
| `gprop` | `news` | Googleニュース |
| `hl` | `ja` | UI言語（日本語） |

過去7日間・日本・YouTube・日本語UIならこうなる。

```
https://trends.google.co.jp/trends/explore?date=now%207-d&geo=JP&gprop=youtube&hl=ja
```

スペースは`%20`にエンコード。`today`系は月単位、`now`系は時間〜日単位の相対指定。

---

## 5. Browser Use CLIの基本コマンドリファレンス

検証で実用に耐えたコマンドはこれだけ。

### 基本操作

| コマンド | 用途 |
|---|---|
| `browser-use open "URL"` | ページを開く |
| `browser-use get title` | ページタイトル取得（疎通確認用） |
| `browser-use get text` | innerText取得。SPAでは空が返ることが多い |
| `browser-use eval "JSコード"` | JavaScriptを直接実行。データ抽出の主力 |
| `browser-use state` | アクセシビリティツリー取得 |
| `browser-use screenshot` | スクリーンショット保存 |
| `browser-use close` | ブラウザを閉じる |

### 操作系

| コマンド | 用途 |
|---|---|
| `browser-use scroll down` | 下スクロール（追加描画トリガー） |
| `browser-use scroll up` | 上スクロール |
| `browser-use click "セレクタ"` | 要素クリック |
| `browser-use type "テキスト"` | テキスト入力 |

### セッション管理

| コマンド | 用途 |
|---|---|
| `browser-use --session 1 open "URL"` | セッション1でページを開く |
| `browser-use --session 2 open "URL"` | セッション2を並列で開く |
| `browser-use --profile "<Chromeプロファイルパス>" open "URL"` | 実Chromeプロファイルを使う |

---

## 6. 取得フロー実装

実行順はこう。

```bash
# 1. 「探す」タブをYouTube・過去1ヶ月・日本で開く
browser-use open "https://trends.google.co.jp/trends/explore?date=today%201-m&geo=JP&gprop=youtube&hl=ja"

# 2. 12秒待機（JS描画のため）
sleep 12

# 3. タイトル確認（"探す - Google トレンド" が返ればOK）
browser-use get title

# 4. innerText一括取得
browser-use eval "document.body.innerText"

# 5. 取得結果が薄い場合のみスクロールして追加描画
browser-use scroll down
browser-use scroll down
browser-use eval "document.body.innerText"

# 6. 終了
browser-use close
```

`get text`ではなく`eval "document.body.innerText"`を使う理由は、SPAで動的注入されたコンテンツが`get text`では拾えないケースが頻発したため。

<!-- 画像案②: 上記コマンドを順に実行しているターミナルのスクショ。タイトル"探す - Google トレンド"とinnerTextの一部が見えると良い -->

### なぜPythonスクリプトを挟まないか

1. 取得結果がランキングという単純構造で、ロジック分岐が不要
2. Googleトレンドのレイアウトは時折変わり、固定パーサより自然言語抽出のほうが頑健
3. 出力がMarkdownリストで完結し、Excel化が不要

LLMが整形に向いている範囲はLLMに残すほうがメンテが楽。

---

## 7. ハマりどころ①：JS描画待ちは12秒必要

GoogleトレンドはSPAで、HTMLレスポンス直後のDOMにはキーワードがほぼ存在せず、Reactで後から差し込まれる。実測では`sleep 3`はヘッダーだけ、`sleep 5`は半分空、`sleep 8`でほぼ取れる、`sleep 12`で安定。

```bash
browser-use open "https://trends.google.co.jp/trends/explore?date=today%201-m&geo=JP&gprop=youtube&hl=ja"
sleep 12  # 8秒未満は不安定。12秒で安定
browser-use eval "document.body.innerText"
```

遅い回線では`sleep 15`。`state`で完了判定するのが理論的には正しいが、Googleトレンドは継続的にXHRを叩いていて`state`では完了が出ない。固定秒スリープが現実解。

---

## 8. ハマりどころ②：`get text`が空を返す

`browser-use get text`はPlaywrightの`page.text_content('body')`相当。Shadow DOMやReact内部ツリーにテキストが入るケースで拾い損ねる。対処は`eval`に切り替えるだけ。

```bash
# NG: 空が返ることが多い
browser-use get text

# OK: innerTextで明示的に取る
browser-use eval "document.body.innerText"
```

`innerText`は表示中テキストを返すプロパティで、`textContent`より人間の視認内容に近い。それでも空なら、スクロールして再取得。

```bash
browser-use scroll down
browser-use scroll down
browser-use scroll down
browser-use eval "document.body.innerText"
```

---

## 9. ハマりどころ③：403/Captchaとアンチボット対策

連続リクエストやデフォルトセッションのまま叩き続けると、Captchaが出る。403やリダイレクトも返る。対策は2つ。

### A. リクエスト間隔を空ける

最低5秒、推奨10秒以上。連続実行スクリプトでは`time.sleep(10)`を必ず挟む。

### B. 実Chromeプロファイルを使う

`--profile`で普段使いのプロファイルを指定する。

```bash
# macOS
browser-use --profile "$HOME/Library/Application Support/Google/Chrome/Default" open "https://trends.google.co.jp/trends/explore?date=today%201-m&geo=JP&gprop=youtube&hl=ja"

# Windows
browser-use --profile "%LOCALAPPDATA%\Google\Chrome\User Data\Default" open "https://trends.google.co.jp/trends/explore?date=today%201-m&geo=JP&gprop=youtube&hl=ja"
```

落とし穴はChromeプロファイルの排他制御。

---

## 10. ハマりどころ④：Chromeプロファイルの排他制御

`--profile`で指定したプロファイルが普段使いのChromeで開かれていると、Chromeの`Singleton`ロックに弾かれて起動失敗する。`SingletonLock`や`profile is already in use`のエラーが出たらこれ。

対処はChromeを完全終了してから`browser-use`を実行。タスクトレイ常駐も切る。タブを閉じるだけでは不十分で、プロセスが残るとロックは解けない。

```bash
# macOS で確認
pgrep -f "Google Chrome"

# プロセスが残っていれば終了
osascript -e 'quit app "Google Chrome"'
```

実運用では自動化用に別プロファイル（例：`Profile 2`）を切り、Googleにログインしてから`--profile`指定するのが安全。普段使いと共存できる。

```bash
browser-use --profile "$HOME/Library/Application Support/Google/Chrome/Profile 2" open "..."
```

---

## 11. ハマりどころ⑤：`get title`は通っても`eval`が空

タイトルは返るのに、`eval`の`innerText`がヘッダー部分しか返らない症状。タイトルは`<title>`タグでSSRされ、本体キーワードリストはクライアントサイドJSが描画するため起きる。

`get title`は疎通確認専用、本体取得は`eval` + 十分なスリープ、と役割を分ける。

---

## 12. ハマりどころ総まとめ

| 症状 | 原因 | 対処 |
|---|---|---|
| `eval`の結果がヘッダーだけ | JS描画が完了していない | `sleep 12`を必ず挟む |
| `browser-use get text`が空 | SPAでtext_contentが拾えない | `eval "document.body.innerText"`に切り替え |
| 403/Captchaが出る | アンチボット検知 | リクエスト間隔10秒、`--profile`で実Chrome |
| `--profile`指定で起動失敗 | Chrome起動中で排他ロック | Chrome完全終了、または別プロファイル運用 |
| キーワードが5件しか取れない | 遅延描画分が未取得 | `scroll down`を3〜5回挟んで再`eval` |
| `get title`は通るが`eval`が薄い | SSRとCSRの混在 | タイトルは疎通確認用と割り切る |

---

## 13. スキル化：SKILL.md + reference.mdの構成

Claude Codeのスキルとしてパッケージ化する。配置は`~/.claude/skills/browser-use-googletrends/`。

```
browser-use-googletrends/
├── SKILL.md       # トリガー定義、基本フロー、エラーマトリクス
└── reference.md   # コマンド全リスト、URLパラメータ仕様、アンチボット対策
```

`SKILL.md`のフロントマターでトリガーを定義。

```yaml
---
name: browser-use-cli
version: 1.1.0
description: >
  Browser Use CLI を使ってブラウザを自動操作するスキル。
  Google トレンド「探す」タブでのYouTube検索トレンド取得を主なユースケースとし、
  コマンドライン経由でブラウザを操作する手順を定義する。
triggers:
  - browser-use
  - ブラウザ自動操作
  - Google トレンド
  - YouTubeトレンド
  - YouTube検索トレンド
  - 急上昇キーワード
  - トレンド取得
  - スクレイピング
tags:
  - browser-use
  - cli
  - scraping
  - google-trends
  - automation
---
```

本体（`SKILL.md`）は実行フローと最小コマンドだけ。詳細仕様は`reference.md`に分離する。初期コンテキストに乗るのは`SKILL.md`だけで、`reference.md`は必要時にClaude自身が`Read`する。

### なぜ分離するか

`SKILL.md`は発動時に毎回読まれる。2万字のリファレンスを詰めるとトークンコストが跳ねる。SKILL本体は3〜400字、リファレンスは別ファイル、がClaude Codeスキルの標準作法。

### 出力フォーマットを固定する

```markdown
## 出力フォーマット

## Google トレンド YouTubeキーワード（日本・過去1ヶ月）
取得日時：YYYY/MM/DD HH:MM

1. キーワードA
2. キーワードB
3. キーワードC
...（上位50件）
```

指定がないとClaudeが余計な解説や絵文字を入れる。固定フォーマットなら後段の集計スクリプトでパースしやすい。

<!-- 画像案③: Claude Codeで「YouTubeトレンドを取得して」と打って、スキルが発動し、整形済みリストが返ってくるまでのスクショ -->

---

## 14. 毎週運用のかたち

月曜朝に自然言語で叩き、結果をNotionに転記する運用にしている。

```
ユーザー: YouTubeトレンドを過去7日間で取得して
Claude:   （スキル発動 → browser-use → 整形）
          ## Google トレンド YouTubeキーワード（日本・過去7日間）
          取得日時：2026/05/24 09:12
          1. ...
```

期間切替は自然言語に任せる。「過去1ヶ月」「過去7日間」「過去12ヶ月」をClaudeが`date`パラメータに変換する。`today 1-m` / `now 7-d` / `today 12-m`の対応表を`SKILL.md`に書いておけばよい。

YouTube Data API v3との使い分けはこう。

| 知りたいこと | 使うAPI |
|---|---|
| いま何が検索されているか（企画ネタ） | Googleトレンド `/explore?gprop=youtube` |
| いま何が再生されているか（参考動画探し） | YouTube Data API v3 `videos.list?chart=mostPopular` |
| 自分のチャンネルの伸び | YouTube Analytics API |

検索クエリ視点のトレンドは公式API化されておらず、ブラウザ自動化が現状の唯一解。

---

## 15. 計測結果

実測値。

| 項目 | 値 |
|---|---|
| 1回の取得時間 | 約20秒。open 1秒 + sleep 12秒 + eval 1秒 + 整形 |
| 取得件数 | 上位30〜50件（スクロール込みで安定して50件超え） |
| 失敗率 | スリープ12秒固定で約5%。スクロール込みで1%以下 |
| 403/Captcha遭遇率 | 連続実行で30回に1回程度。`--profile`使用で月1回未満 |
| トークンコスト | スキル発動1回あたり数円程度 |

週1回・1分以内で終わる作業なので、cron化はせず月曜朝に手で叩くフローに落ち着いた。

---

## 16. 横展開できそうな対象

- Googleトレンド`gprop=images`版（画像検索トレンド）
- Googleトレンド`gprop=news`版（ニュース検索トレンド）
- 各国版`geo=US` / `geo=KR`などのローカルトレンド
- Amazonの売れ筋ランキング（カテゴリパラメータ解析）
- メルカリ・ヤフオクのカテゴリ別検索トレンド
- 求人系の人気職種ランキング

公式API化されておらず、SPA構造でURLパラメータ絞り込みが効くページなら、`open → sleep → eval → close`パターンがほぼ流用できる。

---

## 17. 利用上の注意

Googleトレンドの利用規約はGoogle一般利用規約に従う。スクレイピング禁止の明文は2026年5月時点で確認できないが、以下を守って運用している。

- アクセス間隔は最低5秒、推奨10秒以上
- 取得データの第三者販売はしない
- 取得結果は社内リサーチ補助に限定
- 大量並列アクセスはしない（`--session`を10並列にしない）

アンチボットが強く効くサービスなので、Captchaを連発する使い方は続かない。節度ある使用が長期運用につながる。

---

## まとめ

YouTube検索トレンドは公式APIで取れない情報の代表例。Googleトレンドの`/explore?gprop=youtube`をBrowser Use CLIで安定取得し、Claude Codeスキルとしてチーム配布できる形にまとめた。

ポイント。

1. `videos.list?chart=mostPopular`と検索トレンドは別物
2. SPA相手は`sleep 12` + `eval "document.body.innerText"`が最小実用単位
3. Chromeプロファイル排他制御に注意。自動化用に別プロファイルを切る

Browser Use CLIで小さなコマンドの組み合わせに落とせば、再現性ある作業手順として共有しやすい。SKILL.md + reference.mdの2ファイル構成ならトークンコストも抑えられる。

スキルリポジトリ（browser-use-googletrends）：[GitHub URL]

---

## 参考

- Google トレンド: https://trends.google.co.jp/trends/explore
- Browser Use CLI: https://docs.browser-use.com/open-source/browser-use-cli
- YouTube Data API v3: https://developers.google.com/youtube/v3
- Playwright: https://playwright.dev/python/

---

**Zenn想定タグ**：`claude-code` `browser-use` `automation` `python` `scraping`
**Qiita想定タグ**：`ClaudeCode` `BrowserUse` `自動化` `スクレイピング` `Python`
