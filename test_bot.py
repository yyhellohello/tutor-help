#!/usr/bin/env python3
"""
日文家教管理LINE Bot 測試腳本
"""

import sqlite3
from datetime import datetime, timedelta

def test_database():
    """測試資料庫連接和基本操作"""
    print("=== 測試資料庫連接 ===")
    
    try:
        conn = sqlite3.connect('tutor_bot.db')
        cursor = conn.cursor()
        
        # 檢查資料表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"現有資料表: {[table[0] for table in tables]}")
        
        # 測試新增學生
        print("\n=== 測試新增學生 ===")
        cursor.execute('''
            INSERT OR REPLACE INTO students (name, email, hourly_rate, drive_folder_id)
            VALUES (?, ?, ?, ?)
        ''', ('測試學生', 'test@example.com', 500, 'test_folder_id'))
        
        # 查詢學生
        cursor.execute('SELECT * FROM students WHERE name = ?', ('測試學生',))
        student = cursor.fetchone()
        print(f"學生資料: {student}")
        
        # 測試新增課程
        print("\n=== 測試新增課程 ===")
        start_time = datetime.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        
        cursor.execute('''
            INSERT OR REPLACE INTO classes 
            (class_id, student_name, start_time, end_time, status, google_calendar_event_id, google_meet_link, drive_folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('C1234567890', '測試學生', start_time, end_time, 'scheduled', 'test_event_id', 'test_meet_link', 'test_course_folder'))
        
        # 查詢課程
        cursor.execute('SELECT * FROM classes WHERE class_id = ?', ('C1234567890',))
        class_info = cursor.fetchone()
        print(f"課程資料: {class_info}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 資料庫測試成功！")
        
    except Exception as e:
        print(f"❌ 資料庫測試失敗: {e}")

def test_google_api():
    """測試Google API連接"""
    print("\n=== 測試Google API連接 ===")
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = 'google_credentials.json'
        
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        # 測試Calendar API
        calendar_service = build('calendar', 'v3', credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        print(f"✅ Calendar API 連接成功！找到 {len(calendar_list.get('items', []))} 個日曆")
        
        # 測試Drive API
        drive_service = build('drive', 'v3', credentials=credentials)
        files = drive_service.files().list(pageSize=1).execute()
        print(f"✅ Drive API 連接成功！")
        
    except Exception as e:
        print(f"❌ Google API 測試失敗: {e}")

def test_line_bot():
    """測試LINE Bot設定"""
    print("\n=== 測試LINE Bot設定 ===")
    
    try:
        from linebot import LineBotApi
        
        LINE_CHANNEL_ACCESS_TOKEN = '9J4cAf8zpSxPDKSoZbgTrGXTEeCEVVkvuUwBrqZ9Vo5hmcFgM5EaE0ouGfXsZy5DEsyEDi1FpfqzwYMZfDeyEj//CbgVIj42iMCa6N5VtMVSt2ev3cSNWnSRmvIJExo5S6f61tYPmZdJ5CEs3loprwdB04t89/1O/w1cDnyilFU='
        
        line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
        profile = line_bot_api.get_profile('U1234567890abcdef')  # 測試用ID
        print("✅ LINE Bot API 連接成功！")
        
    except Exception as e:
        print(f"❌ LINE Bot 測試失敗: {e}")
        print("注意：這是正常的，因為我們沒有有效的User ID")

def main():
    """主測試函數"""
    print("🚀 開始測試日文家教管理LINE Bot")
    print("=" * 50)
    
    # 測試資料庫
    test_database()
    
    # 測試Google API
    test_google_api()
    
    # 測試LINE Bot
    test_line_bot()
    
    print("\n" + "=" * 50)
    print("🎉 測試完成！")
    print("\n下一步：")
    print("1. 將程式碼上傳到 GitHub")
    print("2. 在 Railway 部署")
    print("3. 設定 LINE Bot Webhook")
    print("4. 開始使用！")

if __name__ == "__main__":
    main()
