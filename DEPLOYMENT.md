# 部署指南

## 1. 準備工作

### 1.1 建立 GitHub Repository
1. 前往 [GitHub.com](https://github.com)
2. 點擊 "New repository"
3. Repository 名稱：`japanese-tutor-bot`
4. 選擇 "Public"
5. 不要勾選 "Add a README file"

### 1.2 上傳程式碼到 GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yyhellohello/japanese-tutor-bot.git
git push -u origin main
```

## 2. Railway 部署（推薦）

### 2.1 註冊 Railway
1. 前往 [Railway.app](https://railway.app)
2. 使用 GitHub 帳號登入

### 2.2 部署專案
1. 點擊 "New Project"
2. 選擇 "Deploy from GitHub repo"
3. 選擇 `japanese-tutor-bot` repository
4. 點擊 "Deploy Now"

### 2.3 設定環境變數
在 Railway 專案設定中，前往 "Variables" 標籤，新增以下環境變數：

```
LINE_CHANNEL_SECRET=d2be7216d3a0cf571c96f45b23dfc01d
LINE_CHANNEL_ACCESS_TOKEN=9J4cAf8zpSxPDKSoZbgTrGXTEeCEVVkvuUwBrqZ9Vo5hmcFgM5EaE0ouGfXsZy5DEsyEDi1FpfqzwYMZfDeyEj//CbgVIj42iMCa6N5VtMVSt2ev3cSNWnSRmvIJExo5S6f61tYPmZdJ5CEs3loprwdB04t89/1O/w1cDnyilFU=
CALENDAR_ID=forget775981@gmail.com
DRIVE_ROOT_FOLDER_ID=1--LlRPbaE0vbo62N__kI_5VqnfRbWCpH
```

### 2.4 設定 Google API 憑證
將 `google_credentials.json` 的內容複製到環境變數：
```
GOOGLE_CREDENTIALS={"type":"service_account","project_id":"tutor-help-470006",...}
```

### 2.5 獲取部署網址
部署完成後，Railway 會提供一個網址，例如：
`https://japanese-tutor-bot-production.up.railway.app`

## 3. LINE Bot Webhook 設定

### 3.1 設定 Webhook URL
1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 選擇您的 Provider 和 Channel
3. 前往 "Messaging API" 設定
4. 在 "Webhook URL" 欄位輸入：
   `https://japanese-tutor-bot-production.up.railway.app/callback`
5. 開啟 "Use webhook"
6. 點擊 "Verify" 測試連接

### 3.2 設定 LINE Bot 回應模式
1. 在 "Messaging API" 設定中
2. 關閉 "Auto-reply messages"
3. 關閉 "Greeting messages"

## 4. Google Calendar 權限設定

### 4.1 分享日曆給服務帳戶
1. 開啟您的 Google Calendar
2. 在左側找到您的日曆
3. 點擊日曆旁邊的三個點 → "設定和共用"
4. 在 "與特定人員共用" 中點擊 "+ 新增人員"
5. 輸入服務帳戶電子郵件：`id-179@tutor-help-470006.iam.gserviceaccount.com`
6. 設定權限為 "變更和管理共用設定"

## 5. 測試部署

### 5.1 基本功能測試
1. 在 LINE 中搜尋您的官方帳號並加為好友
2. 發送 "新增學生 測試學生 test@example.com 500"
3. 檢查是否收到確認訊息

### 5.2 排課測試
1. 發送 "排課 測試學生 2024-01-15 14:00 15:00"
2. 檢查是否收到課程編號和 Google Meet 連結

## 6. 故障排除

### 6.1 常見問題
1. **Webhook 驗證失敗**：檢查 URL 是否正確
2. **Google API 錯誤**：檢查憑證和權限設定
3. **部署失敗**：檢查 requirements.txt 和 Python 版本

### 6.2 查看日誌
在 Railway 中：
1. 前往專案頁面
2. 點擊 "Deployments" 標籤
3. 查看最新的部署日誌

## 7. 備份和維護

### 7.1 資料庫備份
SQLite 資料庫檔案會自動保存在 Railway 中，但建議定期備份：
1. 在 Railway 中下載 `tutor_bot.db` 檔案
2. 儲存到本地電腦

### 7.2 程式碼更新
當您修改程式碼時：
```bash
git add .
git commit -m "Update description"
git push origin main
```
Railway 會自動重新部署。

## 8. 費用說明

### 8.1 Railway 免費額度
- 每月 $5 免費額度
- 對於小型應用程式通常足夠
- 超過免費額度會收費

### 8.2 監控使用量
在 Railway 儀表板中可以查看：
- CPU 使用量
- 記憶體使用量
- 網路流量
- 費用預估

## 9. 安全性注意事項

1. **不要將憑證上傳到公開 Repository**
2. **定期更新 API 憑證**
3. **監控應用程式日誌**
4. **設定適當的存取權限**

## 10. 支援

如果遇到問題：
1. 檢查 Railway 部署日誌
2. 檢查 LINE Bot Webhook 設定
3. 檢查 Google API 權限
4. 查看 README.md 中的故障排除指南
