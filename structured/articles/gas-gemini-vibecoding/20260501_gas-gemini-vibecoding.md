---
タイトル: GAS × Gemini バイブコーディング 注意点
状態: stub
---

# GAS × Gemini バイブコーディング 注意点

## 参考リソース

1. [G-Gen - Gemini APIキーの不正使用問題と対策](https://blog.g-gen.co.jp/entry/gemini-api-abuse-explanation-and-prevention)
2. [gicloud Note - GAS Advanced Service に Vertex AI Service 追加（2026-01-12）](https://note.com/gicloud/n/n2ba28fe871ef)
   - APIキーなし・プロジェクト連結不要で Gemini API に安全アクセス可能に
3. [yoshidumi - GASの制限値と解決策](https://www.yoshidumi.co.jp/collaboration-lab/gas-quotas-and-solutions)

## 要点メモ

- APIキーをスクリプトに直書きすると不正利用リスクあり → Vertex AI Service 経由が安全
- GASのクォータ制限（実行時間・API呼び出し回数）に注意
- 詳細は後から追記
