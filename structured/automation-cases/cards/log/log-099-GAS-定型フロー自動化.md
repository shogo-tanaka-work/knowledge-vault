---
id: log-099
tier: 2
category: [定型フロー自動化]
tools: [GAS, Gemini, NotebookLM]
primary_tool: "GAS"
primary_category: "定型フロー自動化"
quant_effect: ""
source_sheet: 業務系の面談ログ_Gen
source_row: 799
source_csv_id: 0798
published_axes: []  # TODO
---
# GASで退職金掛金計算を自動化し手作業削減

> ⚠ 2軍カード。元データは面談メモのため Before/After 列はなし。
> 講師所感と定性効果から再構成し、発信時に汎化済み Before/After を起こすこと。

## AI判定サマリ
- 判定理由: 退職金計算自動化実装
- 一行サマリ: GASで退職金掛金計算を自動化し手作業削減

## 定量効果

(記載なし)

## 定性効果（元データ）

NotebookLMで過去面談記録の活用が成功。退職金掛金計算の自動化により毎年の手作業を削減予定

## 特記事項・講師所感（元データ）

GASを選択した理由は計算正確性と定期実行機能。Geminiではなく確定的な処理が必要。要件定義では情報スコープの絞り込みと段階的アプローチ（正社員版→パート版）を強調。変更対象者のみを出力する仕様で実装

## 業務課題カテゴリ

定型フロー自動化

## 使用AIツール

GAS, Gemini, NotebookLM

## 汎用化Tips

<!-- TODO -->

## 発信角度の候補

<!-- TODO: note / X / Threads / LinkedIn / 技術ブログ -->
