# automation-cases

Claudeマスター講座などで講師が伴走した「業務自動化の実例」を、個人名・社名・固有業界名を伏せた一般論として整理した素材ライブラリ。`10_プロジェクト/` 配下の各発信プロジェクト（note / X / Threads / LinkedIn / 技術ブログ）から共通参照する。

## 構造

```
automation-cases/
├── source/
│   ├── 講師面談ログDB は配置せず、~/Downloads/ から都度読み込む
│   ├── extract.py             … xlsx → 匿名化済み統合CSV
│   ├── anonymize_dict.json    … 社名等のマスク辞書（差分実行で資産化）
│   └── automation-cases.csv   … 4シート統合・全件・匿名化済み
├── scripts/
│   └── generate_cards.py      … CSV → カード雛形 + INDEX.md
├── cards/
│   ├── INDEX.md               … 1軍索引（成果報告DB系）
│   ├── NNN-<tool>-<category>.md … 1軍カード（34件、Before/After完備）
│   └── log/
│       ├── INDEX.md           … 2軍索引（面談ログ由来）
│       └── log-NNN-*.md       … 2軍カード（249件、AI評価YES）
└── README.md（このファイル）
```

## データソース

`~/Downloads/講師面談ログDB.xlsx`（4シート計1487件）

| シート | 件数 | 性質 |
|---|---|---|
| 業務成果報告DB | 28 | 完成事例（Before/After/定量効果あり） |
| Biz成果報告DB | 7 | 完成事例（ビジネス職向け） |
| 業務系の面談ログ_Gen | 1058 | 進行中含む面談メモ |
| 業務系の面談ログ_Biz | 394 | 同上（ビジネス職向け） |

## 匿名化方針

- `受講生名` `担当講師名` `投稿者` 等は CSV に出さない
- 本文中の固有名詞は `extract.py` で機械置換
  - 個人名: xlsxから収集した受講生・講師名リストを全件マスク
  - 社名: 法人格パターン（株式会社など）＋ `anonymize_dict.json` で辞書管理
- 業界名は「放送業界 → 映像系制作の現場」のような汎化が必要だが、機械では困難なので**カードの人手レビューで処理**する
- CSV/カード生成のたびに残存チェックを行う（`extract.py` の出力JSONで確認）

## カード化フェーズ

- **フェーズ1（自動生成済み）**: 成果報告DB系 計34件 → `cards/001.md`〜`034.md`
  - Before / After / 定量効果 / 定性効果 / 特記事項 / 社内展開 は埋まっている
  - **タイトル / 汎用化Tips / 発信角度** は TODO（人手加筆）
- **フェーズ2（自動生成済み）**: 面談ログから「改善成功×80字以上」654件をAI評価し YES 249件を2軍カード化 → `cards/log/log-001.md`〜`log-249.md`
  - 元データに Before/After 列がないため、定性効果＋特記事項からの再構成
  - **発信時に汎化済み Before/After を人手で起こす前提**
  - 評価詳細は `source/verdict_batch_*.jsonl`
- **フェーズ3（未着手）**: 各カードに対し、媒体別のドラフトを `10_プロジェクト/<各発信>/20_articles/` 配下に展開

## 更新フロー

1. xlsx を最新化したら `python source/extract.py` を再実行
2. 新規行があれば `python scripts/generate_cards.py` でカード雛形が増える
   - 既存カードは上書きされるので、人手加筆済みのものは別ファイル名へリネームしておくか、`generate_cards.py` の上書き判定を将来追加する
3. 残存マスク漏れを見つけたら `anonymize_dict.json` に追記して再実行

## 関連

- 検証ログ: 別軸（`structured/tools/` に検証単位で蓄積）
- 発信プロジェクト: `10_プロジェクト/{note発信, X発信, Threads発信, LinkedIn発信, 技術ブログ発信}/20_articles/`
