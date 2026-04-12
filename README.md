# PokeCard Asset 🃏

個人用ポケモンカードBOX資産管理アプリ。  
スニダン相場と森森買取価格をリアルタイムで取得し、資産を一元管理します。

## 機能
- 保有BOXの登録・数量管理・削除
- スニダン相場 / 森森買取価格の自動取得
- 前回比・累計増減の表示
- iPhone 15 Plus（430px）最適化UI

## セットアップ

```bash
git clone <your-repo>
cd pokecardapp
pip install -r requirements.txt
streamlit run app.py
```

## デプロイ（Streamlit Community Cloud / 無料）

1. このリポジトリをGitHubにpush
2. https://share.streamlit.io にログイン
3. 「New app」→ リポジトリ選択 → `app.py` を指定 → Deploy

## 新しいBOXのURL設定方法

`master_data.py` の対象パックに以下を設定：

```python
"snkrdunk_id": "721913",   # スニダンURLの /apparels/{ここの数字}
"morimori_url": "https://www.morimori-kaitori.jp/category/XXXX/product/YYYY",
```

URLが未設定（None）の場合、価格取得はスキップされ手動での確認が必要です。

## ファイル構成

```
pokecardapp/
├── app.py           # Streamlit UI メイン
├── scraper.py       # スニダン・森森 価格取得
├── database.py      # SQLite操作
├── master_data.py   # 全パックマスタ（cardrush準拠）
├── requirements.txt
└── pokecardapp.db   # 自動生成（gitignore推奨）
```
