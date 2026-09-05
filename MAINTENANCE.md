# 維護說明

## 來源與成品

`drafts/common.md` 與六份濾鏡文件是提示詞的維護來源。修改共用規則只需編輯一處；不要直接修改 `dist/` 中的產物。

[封裝腳本](scripts/package_skills.py) 維護介面描述，將共用契約與單一濾鏡展開成完整 SKILL.md，另產生 agents/openai.yaml。各份設定 `allow_implicit_invocation: false`，維持使用者明確呼叫。

每份成品包含 SKILL.md、介面設定與 LICENSE；授權文字統一來自根目錄 LICENSE。封裝程式、測試與研究材料不進入 ZIP。腳本不安裝、發布或呼叫模型。

## 重建與檢查

在專案根目錄執行：

```powershell
python -X utf8 scripts/package_skills.py
python -X utf8 scripts/package_skills.py --check
python -B -X utf8 -m unittest discover -s tests -v
```

只需 Python 標準函式庫。ZIP 檔案時間固定，讓相同來源在同一環境產生相同位元組；`--check` 可檢查成品與 ZIP 是否偏離來源，不寫檔。`-B` 避免測試產生 Python 快取。

三個封裝測試涵蓋：完整定稿內容、手動政策與每份成品的 MIT 授權、成品被改動時檢查失敗且不覆寫、ZIP 重建一致及損壞偵測。這些檢查不證明模型判斷品質或安裝後的 Host 行為。

## 提交範圍

提交維護來源、封裝腳本、可重跑測試、說明與成品。研究素材、一次性實驗及交接紀錄由 .gitignore 排除，保留在本機；維護流程不依賴這些檔案。
