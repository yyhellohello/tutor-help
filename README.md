# 日文家教管理LINE Bot

這是一個專為日文家教設計的LINE聊天機器人，可以自動化管理學生預約、課程通知、Google Meet連結和費用結算。

## 功能特色

### 1. 學生管理
- 新增學生資訊（姓名、郵件、費用）
- 自動建立Google Drive專屬資料夾
- 支援既有學生資料夾連結

### 2. 課程排程
- 自動建立Google Calendar事件
- 自動生成Google Meet會議連結
- 自動建立課程資料夾
- 課程編號管理

### 3. 課程管理
- 查詢課程資訊
- 修改課程時間
- 取消課程
- 完成課程確認

### 4. 自動化功能
- 每日課程提醒
- 課前10分鐘提醒
- 月費自動計算
- 繳費通知生成

## 使用指令

### 學生管理
```
新增學生 <姓名> <郵件> <費用> [雲端資料夾連結]
```

### 課程排程
```
排課 <學生姓名> <開始時間> <結束時間>
```
時間格式：YYYY-MM-DD HH:MM

### 課程查詢
```
查詢 <課程編號>
```

### 費用計算
```
月費計算
```

## 部署說明

### 1. 環境需求
- Python 3.11+
- LINE Bot API 憑證
- Google Calendar API 憑證
- Google Drive API 憑證

### 2. 本地開發
```bash
pip install -r requirements.txt
python app.py
```

### 3. 雲端部署
推薦使用 Railway 或 Render 進行部署：

1. 將程式碼上傳到 GitHub
2. 在雲端平台連接 GitHub Repository
3. 設定環境變數
4. 部署應用程式

## 環境變數設定

在雲端平台需要設定以下環境變數：

- `LINE_CHANNEL_SECRET`: LINE Bot Channel Secret
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Bot Channel Access Token
- `GOOGLE_CREDENTIALS`: Google API 憑證 JSON 內容
- `CALENDAR_ID`: Google Calendar ID
- `DRIVE_ROOT_FOLDER_ID`: Google Drive 根資料夾 ID

## 資料庫結構

### students 表
- id: 主鍵
- name: 學生姓名
- email: 學生郵件
- hourly_rate: 每小時費用
- drive_folder_id: Google Drive 資料夾 ID
- created_at: 建立時間

### classes 表
- id: 主鍵
- class_id: 課程編號
- student_name: 學生姓名
- start_time: 開始時間
- end_time: 結束時間
- status: 課程狀態 (scheduled/completed/cancelled)
- google_calendar_event_id: Google Calendar 事件 ID
- google_meet_link: Google Meet 連結
- drive_folder_id: 課程資料夾 ID
- created_at: 建立時間

## 注意事項

1. 請確保 Google Calendar 已分享給服務帳戶
2. 請確保 Google Drive 根資料夾權限設定正確
3. 課程編號格式為 C + 時間戳記
4. 只有完成狀態的課程才會計入費用

## 技術架構

- **後端框架**: Flask
- **資料庫**: SQLite
- **LINE Bot SDK**: line-bot-sdk
- **Google API**: google-api-python-client
- **部署**: Gunicorn + Railway/Render

## 授權

本專案僅供個人使用，請勿用於商業用途。
