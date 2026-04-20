# Microsoft Copilot 料金プラン リサーチログ（個人・法人）

> ステータス: 検証中
> 作成日: 2026/04/20
> 最終更新: 2026/04/20
> ファイルパス: /Users/shogo/ObsidianVault/knowledge-vault/structured/tools/20260420_microsoft-copilot-pricing.md

---

## 📋 検証概要

- **ツール/サービス名**: Microsoft Copilot（個人・法人向けプラン）
- **検証対象**: 料金プラン・機能範囲の把握（個人・法人それぞれの最適プラン選定）
- **バージョン/リリース日**: 2026年4月時点の最新情報
- **検証期間**: 2026/04/20 -（検証中）
- **検証担当者**: shogo
- **検証ステータス**: 検証中

---

## 1. 背景と検証目的

### なぜこの検証を行うのか
- 個人・法人それぞれでMicrosoft Copilotを活用するにあたり、料金プランの全体像を把握するため
- Copilot Chat単体の無料利用と、有料プランで何が変わるかを整理したい

### 解決したい課題
- Copilot Pro廃止後の現行プラン体系が不明確だった
- Excel・PowerPoint等のOfficeアプリでCopilotを使うために何が必要かを明確にしたい
- 法人向けプランの種類・機能範囲・2026年4月の仕様変更影響を把握したい

### 期待される効果・ビジネスインパクト
- 不要なプランへの課金を避け、用途・規模に合った最小コストプランを選定できる

---

## 2. ツール/機能の基本情報

### 概要
- MicrosoftのAIアシスタント。チャット・画像生成・Web検索連携・Officeアプリ統合が主機能
- 個人向けは「無料Copilot Chat」「Microsoft 365 Personal/Family」「Microsoft 365 Premium」の3層構造

### 提供元
- Microsoft Corporation

### 主要機能
- Copilot Chat（AIチャット・Web検索・画像生成）
- Office内Copilot（Word・Excel・PowerPoint・Outlookでの文章生成・分析・要約）
- Copilot AIエージェント（Microsoft 365 Premium以上）
- Deep Research・Voice機能（Microsoft 365 Premium以上でフル利用）

### 技術スタック・アーキテクチャ
- GPT-4ベースのLLM（OpenAI連携）
- Microsoft 365サービスとの統合基盤

---

## 3. 検証方法

### 検証環境
- **使用アカウント**: 個人Microsoftアカウント
- **プラン/エディション**: 公式サイト情報による料金リサーチ（実機検証は未実施）
- **検証環境**: 公式ドキュメント・報道情報による情報収集

### 検証シナリオ
1. 個人向け料金プランの体系整理
2. 各プランでCopilotを使える範囲の確認
3. Office系アプリ（Excel・PowerPoint等）でCopilotを使う条件の明確化
4. 法人向けプランの体系整理（Business/Enterprise）
5. 2026年4月15日の仕様変更の影響把握

### 前提条件・制約事項
- 情報は2026年4月20日時点。Microsoftのプラン変更により変動する可能性あり

---

## 4. 検証結果

### 定性的評価

#### 機能面の評価
- 無料のCopilot Chatでも基本的なAIチャット・画像生成・Web検索は利用可能
- Office内でCopilotを使うにはMicrosoft 365サブスクリプションが必要
- 2026年3月以降、Microsoft 365 Personal加入者でもCopilot Chat経由でWord/Excel/PowerPointエージェントが順次利用可能に（デスクトップフル機能はPremium推奨）

#### 実用性
- チャットのみ用途：無料プランで十分
- Officeアプリと組み合わせたい：Microsoft 365 Personal（¥2,130/月）が最小コスト
- 高度なAIエージェント・Deep Research等：Microsoft 365 Premium（¥3,200/月）

---

### 定量的評価

#### 個人向け料金プラン一覧（2026年4月時点）

| プラン | 月払い | 年払い | 主な内容 |
|---|---|---|---|
| 無料（Copilot Chat） | ¥0 | ¥0 | チャット・画像生成（制限あり）・Web検索 |
| Microsoft 365 Personal | ¥2,130 | ¥21,300 | 1人用・1TBストレージ・基本Copilot＋Officeアプリ |
| Microsoft 365 Family | ¥2,740 | ¥27,400 | 最大6人共有・6TBストレージ（AI機能は契約者本人のみ） |
| Microsoft 365 Premium | ¥3,200 | ¥32,000 | フルCopilot機能＋高度AIエージェント（旧Copilot Pro相当） |

#### Office系アプリでのCopilot利用条件

| 使いたい機能 | 必要なプラン |
|---|---|
| Copilot Chat（Web版のみ） | 無料 |
| Office内でのCopilot基本機能 | Microsoft 365 Personal以上 |
| Word/Excel/PowerPointエージェント（Chat経由） | Microsoft 365 Personal以上（2026年3月〜順次開放） |
| デスクトップOfficeでのCopilotフル活用 | Microsoft 365 Premium推奨 |

#### ROI試算
- **削減できる工数**:（随時更新）
- **生産性向上**:（随時更新）
- **コスト削減額**:（随時更新）
- **投資回収期間**:（随時更新）

---

### 法人向け料金プラン（2026年4月時点）

#### Microsoft 365 Business ベースプラン（Copilotは別途アドオン）

| プラン | 月額換算（年払い） | Officeアプリ | 対象規模 |
|---|---|---|---|
| Business Basic | 約¥750 | Web版のみ | 300ユーザー以下 |
| Business Standard | 約¥1,560 | デスクトップ版込み | 300ユーザー以下 |
| Business Premium | 約¥2,750 | デスクトップ版＋高度セキュリティ | 300ユーザー以下 |

※ Copilot機能は含まれない。利用するには下記アドオンが必要。

#### Microsoft 365 Copilot アドオン（法人向け）

| プラン | 月額（ユーザー/月） | 対象規模 | 購入条件 |
|---|---|---|---|
| Copilot Business（キャンペーン ～2026/6/30） | ¥2,698 | 300ユーザー以下 | Business Basic/Standard/Premium いずれかが必須 |
| Copilot Business（通常価格） | ¥3,148 | 300ユーザー以下 | 同上 |
| Copilot Business（月払い） | ¥3,778 | 300ユーザー以下 | 同上 |
| Microsoft 365 Copilot（大企業向け） | 約¥4,500（$30相当） | 制限なし | Enterprise系ライセンスが必要 |

#### Copilot Chat（無料）vs Copilot Business（有料）の機能比較

| 機能 | Copilot Chat（無料） | Copilot Business（有料） |
|---|---|---|
| エンタープライズデータ保護 | あり | あり |
| Webベースのチャット | あり | あり |
| 社内データ（メール・ファイル）への接続 | なし | **あり** |
| Word/Excel/PowerPoint内統合 | 制限あり（4/15以降さらに縮小） | **フル統合** |
| Teams会議の要約・文字起こし | なし | **あり** |
| Outlookのメール要約・下書き | 一部のみ | **フル機能** |
| カスタムエージェント作成 | なし | **あり** |
| 画像生成 | なし | **あり** |
| リクエスト上限 | 約20回/日 | 実質無制限 |

#### 有料版でのOfficeアプリ別Copilot機能（法人・Copilot Business）

| アプリ | できること |
|---|---|
| Word | 提案書・議事録・報告書の下書き自動生成、自然言語での文書指示 |
| Excel | データ分析・集計を自然言語で指示、関数・条件付き書式のサポート |
| PowerPoint | テキスト指示だけでスライド自動生成 |
| Teams | 会議の自動要約、次のアクション提示、遅刻参加者へのキャッチアップ |
| Outlook | メール自動要約、返信下書き自動生成 |

#### 2026年4月15日 仕様変更の影響（組織規模別）

| 組織規模 | 変更内容 |
|---|---|
| 2,000シート以上（エンタープライズ） | Word・Excel・PowerPoint・OneNoteでのCopilot Chat が**完全廃止**。有料ライセンス必須 |
| 300〜2,000シート未満 | 「Copilot Chat (Basic)」として機能制限が明示される |
| 300シート以下（中小企業） | 「標準アクセス」として一部制限（音声機能非提供・ピーク時制限） |
| **個人向け** | **影響なし** |
| Outlook | 全組織で引き続き利用可能（例外） |

---

## 5. 比較・優位性分析

### 既存ツール/類似サービスとの比較

| 項目 | Microsoft Copilot（Premium） | ChatGPT Plus | Google Gemini Advanced |
|---|---|---|---|
| 月額コスト | ¥3,200 | 約¥3,000 | 約¥2,900 |
| Office統合 | ◎（Word/Excel/PowerPoint等） | △（プラグイン経由） | △（Google Workspace連携） |
| 無料プランの充実度 | ○（Copilot Chat無料） | ○（GPT-4o無料枠あり） | ○（Gemini無料枠あり） |
| 日本語対応 | ○ | ◎ | ○ |

### 優位性
- Microsoft 365と完全統合されているため、既存のOfficeユーザーには親和性が高い
- 無料プランでもCopilot Chatとして基本機能が使える

### 劣位性・懸念点
- Copilot Pro廃止後の再編でプラン体系が複雑化
- Microsoft 365 Familyは料金が高いわりにAI機能は契約者本人のみという制限がある

---

## 6. リスク評価

### セキュリティ

| 評価項目 | 評価 | 詳細 |
|---|---|---|
| データ保管場所 | Microsoft管理 | Azure基盤上 |
| 暗号化 | ○ | Microsoft標準 |
| アクセス制御 | ○ | Microsoftアカウント認証 |
| コンプライアンス | ○ | Microsoft標準ポリシー |

### ベンダーロックインリスク
- Microsoft 365との統合が前提のため、他社サービスへの乗り換えは容易でない

---

## 7. 連携性・拡張性

### 既存システムとの連携

| 連携先 | 方法 | 備考 |
|---|---|---|
| Word / Excel / PowerPoint | ネイティブ統合 | Microsoft 365 Personal以上が必要 |
| Outlook | ネイティブ統合 | メール要約・返信生成 |
| Teams | ネイティブ統合 | 法人向けが主体 |
| Web（copilot.microsoft.com） | ブラウザ | 無料で利用可 |

---

## 9. 学びとナレッジ

### 発見したこと
- **Copilot Proは2025年に廃止**され「Microsoft 365 Premium」に統合済み。単体での新規購入は不可
- 2026年3月以降、Microsoft 365 PersonalユーザーもCopilot Chat経由でOfficeエージェントが順次使えるようになり、PremiumとPersonalの差は縮まっている
- 2026年4月15日より法人向け（2,000シート以上）でWord/Excel/PowerPoint内のCopilot Chatが完全廃止。有料ライセンスが必須に
- **法人向けCopilot Businessのキャンペーン価格（¥2,698/月）は2026年6月30日まで**。7月以降は¥3,148/月に値上がり予定
- 法人向けで唯一、**Outlookだけは全組織で無料のまま継続利用可能**（2026年4月15日以降も）
- **2026年7月に法人向けベースプラン（Business Basic/Standard）も値上げ予定**

### Tips・ベストプラクティス
- チャットのみ利用 → 無料で十分、課金不要
- Officeアプリと組み合わせたいが最小コストで → Microsoft 365 Personal（¥2,130/月）
- 高度なAIエージェントも使いたい → Microsoft 365 Premium（¥3,200/月）

---

## 10. 判定と今後のアクション

### 総合評価
⭐️⭐️⭐️⭐️（完了時に更新）

### 導入判定
- [ ] 即座に導入推奨
- [x] 条件付きで導入可（用途・コストに応じてプランを選択）
- [ ] 追加検証が必要
- [ ] 導入見送り

### 判定理由
- 無料のCopilot Chatは即利用可能で試しやすい
- Office連携を重視するなら Microsoft 365 Personal（月額¥2,130）が費用対効果の高い選択肢
- Copilot Pro相当の機能が必要な場合のみ Premium（¥3,200/月）へ

### 次のステップ
- [ ] 無料プランを実際に試す
- [ ] Microsoft 365 PersonalのCopilot機能を実機で検証
- [ ] 検証終了

---

## 📚 関連リソース

### 公式ドキュメント
- [個人向け Copilot の価格プラン | Microsoft](https://www.microsoft.com/ja-jp/microsoft-365-copilot/pricing/individuals)
- [Microsoft Copilot 個人向けページ](https://www.microsoft.com/ja-jp/microsoft-copilot/for-individuals/)
- [Word, Excel, and PowerPoint Agents - Microsoft Support](https://support.microsoft.com/en-us/topic/get-started-with-word-excel-and-powerpoint-agents-in-microsoft-365-copilot-76691f5e-bb19-4029-a34d-33a00e0a0c4f)
- [Microsoft 365 Copilot Business（法人向け）](https://www.microsoft.com/ja-jp/microsoft-365/business/copilot-for-microsoft-365)
- [Microsoft 365 Copilot 料金ページ（法人向け）](https://www.microsoft.com/ja-jp/microsoft-365-copilot/pricing)

### 参考記事・事例
- [Microsoft 365とCopilot Proを統合した最上位プラン「Microsoft 365 Premium」 - PC Watch](https://pc.watch.impress.co.jp/docs/news/2052262.html)
- [Microsoft 365 CopilotライセンスなしでWord/Excel/PowerPointエージェントが利用可能に](https://art-break.net/tech/?p=25106)
- [追加料金なしでのCopilot提供が縮小（2026年4月15日より）- 窓の杜](https://forest.watch.impress.co.jp/docs/news/2094446.html)
- [Microsoft 365 Copilot Business解説 - LicenseCounter](https://licensecounter.jp/microsoft365/blog/2026/02/copilot-business.html)
- [Copilot Chat vs Copilot Business比較（2026年4月）- Get Support](https://www.getsupport.co.uk/blog/2026-04/microsoft-365-copilot-chat-vs-copilot-business/)
- [Word・Excel・PowerPointのCopilot Chat廃止詳細 - Office Watch](https://office-watch.com/2026/microsoft-removes-copilot-chat-word-excel-powerpoint-april-2026/)
- [2026年7月 Microsoft 365価格改定予告 - DX Media](https://dx-media.inap-vision.co.jp/posts/microsoft-365-price-update-july-2026)

---

✅ メモ・議論ログ
- 2026/04/20: 個人でのCopilot利用を検討するにあたり料金プランをリサーチ。Copilot Pro廃止・Microsoft 365 Premium統合が最大の変更点。
- 2026/04/20: 法人・組織向けプランを追記。2026年4月15日の仕様変更（エンタープライズ向けOffice内Copilot Chat廃止）とキャンペーン価格の期限（6月末）が重要ポイント。

---

## 📝 更新ログ

| 日時 | 更新内容の概要 |
|---|---|
| 2026/04/20 | ファイル作成（init）・公式サイト情報によるリサーチ内容を記入 |
| 2026/04/20 | update: 法人向けプラン（Copilot Business・仕様変更・アプリ別機能）を追記 |
