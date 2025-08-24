import os
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    TemplateSendMessage, ButtonsTemplate, PostbackAction,
    FlexSendMessage, BoxComponent, TextComponent, ButtonComponent
)
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import threading
import time

app = Flask(__name__)

# LINE Bot設定
LINE_CHANNEL_SECRET = 'd2be7216d3a0cf571c96f45b23dfc01d'
LINE_CHANNEL_ACCESS_TOKEN = '9J4cAf8zpSxPDKSoZbgTrGXTEeCEVVkvuUwBrqZ9Vo5hmcFgM5EaE0ouGfXsZy5DEsyEDi1FpfqzwYMZfDeyEj//CbgVIj42iMCa6N5VtMVSt2ev3cSNWnSRmvIJExo5S6f61tYPmZdJ5CEs3loprwdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google API設定
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'google_credentials.json'
CALENDAR_ID = 'forget775981@gmail.com'
DRIVE_ROOT_FOLDER_ID = '1--LlRPbaE0vbo62N__kI_5VqnfRbWCpH'

# 資料庫初始化
def init_database():
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    # 學生資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            hourly_rate INTEGER NOT NULL,
            drive_folder_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 課程資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT UNIQUE NOT NULL,
            student_name TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            status TEXT DEFAULT 'scheduled',
            google_calendar_event_id TEXT,
            google_meet_link TEXT,
            drive_folder_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_name) REFERENCES students (name)
        )
    ''')
    
    conn.commit()
    conn.close()

# Google API服務初始化
def get_google_service(service_name):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build(service_name, 'v3', credentials=credentials)

# 建立Google Meet會議
def create_google_meet(student_name, start_time, end_time):
    try:
        calendar_service = get_google_service('calendar')
        
        event = {
            'summary': f'日文家教 - {student_name}',
            'description': f'與{student_name}的日文家教課程',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Taipei',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f'meet_{int(time.time())}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        
        event = calendar_service.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        return event['id'], event['conferenceData']['entryPoints'][0]['uri']
    except Exception as e:
        print(f"建立Google Meet失敗: {e}")
        return None, None

# 建立Google Drive資料夾
def create_drive_folder(parent_folder_id, folder_name):
    try:
        drive_service = get_google_service('drive')
        
        folder_metadata = {
            'name': folder_name,
            'parents': [parent_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        return folder.get('id')
    except Exception as e:
        print(f"建立Drive資料夾失敗: {e}")
        return None

# 新增學生
def add_student(name, email, hourly_rate, drive_folder_link=None):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        # 檢查學生是否已存在
        cursor.execute('SELECT * FROM students WHERE name = ?', (name,))
        if cursor.fetchone():
            return False, "學生已存在"
        
        drive_folder_id = None
        if drive_folder_link:
            # 從連結中提取資料夾ID
            drive_folder_id = drive_folder_link.split('/')[-1].split('?')[0]
        else:
            # 建立新的學生資料夾
            drive_folder_id = create_drive_folder(DRIVE_ROOT_FOLDER_ID, name)
        
        cursor.execute('''
            INSERT INTO students (name, email, hourly_rate, drive_folder_id)
            VALUES (?, ?, ?, ?)
        ''', (name, email, hourly_rate, drive_folder_id))
        
        conn.commit()
        return True, f"學生{name}已登錄\n上課費用：{hourly_rate}元/小時\n雲端資料夾：{'已設定' if drive_folder_id else '未設定'}"
    except Exception as e:
        return False, f"新增學生失敗: {e}"
    finally:
        conn.close()

# 排課
def schedule_class(student_name, start_time, end_time):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        # 檢查學生是否存在
        cursor.execute('SELECT * FROM students WHERE name = ?', (student_name,))
        student = cursor.fetchone()
        if not student:
            return False, "學生不存在，請先新增學生"
        
        # 生成課程編號
        class_id = f"C{int(time.time())}"
        
        # 建立Google Meet
        calendar_event_id, meet_link = create_google_meet(student_name, start_time, end_time)
        
        # 建立課程資料夾
        course_folder_name = start_time.strftime('%Y-%m-%d')
        drive_service = get_google_service('drive')
        
        # 檢查學生是否有專屬資料夾
        student_drive_folder_id = student[4]  # drive_folder_id
        if not student_drive_folder_id:
            # 建立學生專屬資料夾
            student_drive_folder_id = create_drive_folder(DRIVE_ROOT_FOLDER_ID, student_name)
            cursor.execute('UPDATE students SET drive_folder_id = ? WHERE name = ?', 
                         (student_drive_folder_id, student_name))
        
        # 建立課程資料夾
        course_folder_id = create_drive_folder(student_drive_folder_id, course_folder_name)
        
        # 儲存課程資料
        cursor.execute('''
            INSERT INTO classes (class_id, student_name, start_time, end_time, 
                               google_calendar_event_id, google_meet_link, drive_folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (class_id, student_name, start_time, end_time, 
              calendar_event_id, meet_link, course_folder_id))
        
        # 計算當月累計費用
        cursor.execute('''
            SELECT SUM((julianday(end_time) - julianday(start_time)) * 24) as total_hours
            FROM classes 
            WHERE student_name = ? 
            AND start_time >= date('now', 'start of month')
            AND status = 'completed'
        ''', (student_name,))
        
        total_hours = cursor.fetchone()[0] or 0
        total_cost = total_hours * student[3]  # hourly_rate
        
        conn.commit()
        
        return True, f"{student_name} 已完成排課\n課程編號：{class_id}\n上課時間：{start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}\nGoogle Meet：{'已設定' if meet_link else '設定失敗'}\n雲端資料夾{course_folder_name}：{'已設定' if course_folder_id else '設定失敗'}\n當月累計費用：{total_cost:.0f}元 ({total_hours:.1f}小時)"
    
    except Exception as e:
        return False, f"排課失敗: {e}"
    finally:
        conn.close()

# 查詢課程
def get_class_info(class_id):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT class_id, student_name, start_time, end_time, status
            FROM classes WHERE class_id = ?
        ''', (class_id,))
        
        class_info = cursor.fetchone()
        if not class_info:
            return None
        
        return {
            'class_id': class_info[0],
            'student_name': class_info[1],
            'start_time': class_info[2],
            'end_time': class_info[3],
            'status': class_info[4]
        }
    finally:
        conn.close()

# 修改課程時間
def modify_class_time(class_id, new_start_time, new_end_time):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        # 獲取課程資訊
        cursor.execute('SELECT * FROM classes WHERE class_id = ?', (class_id,))
        class_info = cursor.fetchone()
        if not class_info:
            return False, "課程不存在"
        
        # 更新Google Calendar事件
        calendar_service = get_google_service('calendar')
        event = {
            'start': {
                'dateTime': new_start_time.isoformat(),
                'timeZone': 'Asia/Taipei',
            },
            'end': {
                'dateTime': new_end_time.isoformat(),
                'timeZone': 'Asia/Taipei',
            }
        }
        
        calendar_service.events().update(
            calendarId=CALENDAR_ID,
            eventId=class_info[5],  # google_calendar_event_id
            body=event
        ).execute()
        
        # 刪除舊的課程資料夾
        if class_info[7]:  # drive_folder_id
            drive_service = get_google_service('drive')
            try:
                drive_service.files().delete(fileId=class_info[7]).execute()
            except:
                pass
        
        # 建立新的課程資料夾
        new_course_folder_name = new_start_time.strftime('%Y-%m-%d')
        new_course_folder_id = create_drive_folder(
            class_info[4],  # student's drive folder
            new_course_folder_name
        )
        
        # 更新資料庫
        cursor.execute('''
            UPDATE classes 
            SET start_time = ?, end_time = ?, drive_folder_id = ?
            WHERE class_id = ?
        ''', (new_start_time, new_end_time, new_course_folder_id, class_id))
        
        conn.commit()
        
        return True, f"課程時間已修改\n{class_info[2]} {new_start_time.strftime('%Y-%m-%d %H:%M')} - {new_end_time.strftime('%H:%M')}\nGoogle Meet：已重新設定\n雲端資料夾：已重新建立新的資料夾"
    
    except Exception as e:
        return False, f"修改課程失敗: {e}"
    finally:
        conn.close()

# 取消課程
def cancel_class(class_id):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        # 獲取課程資訊
        cursor.execute('SELECT * FROM classes WHERE class_id = ?', (class_id,))
        class_info = cursor.fetchone()
        if not class_info:
            return False, "課程不存在"
        
        # 取消Google Calendar事件
        if class_info[5]:  # google_calendar_event_id
            calendar_service = get_google_service('calendar')
            try:
                calendar_service.events().delete(
                    calendarId=CALENDAR_ID,
                    eventId=class_info[5]
                ).execute()
            except:
                pass
        
        # 更新課程狀態
        cursor.execute('UPDATE classes SET status = ? WHERE class_id = ?', ('cancelled', class_id))
        
        conn.commit()
        
        return True, f"課程已取消\n{class_info[2]} {class_info[3]}"
    
    except Exception as e:
        return False, f"取消課程失敗: {e}"
    finally:
        conn.close()

# 完成課程
def complete_class(class_id):
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE classes SET status = ? WHERE class_id = ?', ('completed', class_id))
        conn.commit()
        return True, "課程已完成"
    except Exception as e:
        return False, f"完成課程失敗: {e}"
    finally:
        conn.close()

# 計算月費
def calculate_monthly_fee():
    conn = sqlite3.connect('tutor_bot.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT s.name, s.hourly_rate, 
                   SUM((julianday(c.end_time) - julianday(c.start_time)) * 24) as total_hours
            FROM students s
            LEFT JOIN classes c ON s.name = c.student_name 
                AND c.status = 'completed'
                AND c.start_time >= date('now', '-1 month', 'start of month')
                AND c.start_time < date('now', 'start of month')
            GROUP BY s.name, s.hourly_rate
            HAVING total_hours > 0
        ''')
        
        results = cursor.fetchall()
        messages = []
        
        for result in results:
            name, hourly_rate, total_hours = result
            total_cost = total_hours * hourly_rate
            messages.append(f"=== {name} 繳費通知 ===\n哈囉~上個月的費用共{total_cost:.0f}元\n上課時間{total_hours:.1f}小時\n\n再麻煩了~感謝")
        
        return messages
    finally:
        conn.close()

# LINE Bot Webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    if text.startswith('新增學生'):
        # 格式：新增學生 <姓名> <郵件> <費用> [雲端資料夾連結]
        parts = text.split()
        if len(parts) < 4:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式：新增學生 <姓名> <郵件> <費用> [雲端資料夾連結]"))
            return
        
        name = parts[1]
        email = parts[2]
        hourly_rate = int(parts[3])
        drive_folder_link = parts[4] if len(parts) > 4 else None
        
        success, message = add_student(name, email, hourly_rate, drive_folder_link)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    
    elif text.startswith('排課'):
        # 格式：排課 <學生姓名> <開始時間> <結束時間>
        parts = text.split()
        if len(parts) < 4:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式：排課 <學生姓名> <開始時間> <結束時間>\n時間格式：YYYY-MM-DD HH:MM"))
            return
        
        student_name = parts[1]
        try:
            start_time = datetime.strptime(f"{parts[2]} {parts[3]}", "%Y-%m-%d %H:%M")
            end_time = datetime.strptime(f"{parts[2]} {parts[4]}", "%Y-%m-%d %H:%M")
        except:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="時間格式錯誤，請使用：YYYY-MM-DD HH:MM"))
            return
        
        success, message = schedule_class(student_name, start_time, end_time)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    
    elif text.startswith('查詢'):
        # 格式：查詢 <課程編號>
        parts = text.split()
        if len(parts) < 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="格式：查詢 <課程編號>"))
            return
        
        class_id = parts[1]
        class_info = get_class_info(class_id)
        
        if not class_info:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="課程不存在"))
            return
        
        # 建立按鈕模板
        buttons_template = ButtonsTemplate(
            title=f"課程資訊 - {class_id}",
            text=f"學生：{class_info['student_name']}\n上課時間：{class_info['start_time']} - {class_info['end_time']}",
            actions=[
                PostbackAction(label="修改時間", data=f"modify_{class_id}"),
                PostbackAction(label="取消排課", data=f"cancel_{class_id}")
            ]
        )
        
        template_message = TemplateSendMessage(alt_text="課程管理", template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    
    elif text == "月費計算":
        messages = calculate_monthly_fee()
        if not messages:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="本月沒有需要繳費的課程"))
        else:
            for message in messages:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    
    else:
        help_text = """日文家教管理小幫手

可用指令：
1. 新增學生 <姓名> <郵件> <費用> [雲端資料夾連結]
2. 排課 <學生姓名> <開始時間> <結束時間>
3. 查詢 <課程編號>
4. 月費計算

時間格式：YYYY-MM-DD HH:MM"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_text))

# 處理按鈕回覆
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    
    if data.startswith('modify_'):
        class_id = data.split('_')[1]
        # 這裡可以實作修改時間的介面
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"請輸入新的時間格式：修改時間 {class_id} YYYY-MM-DD HH:MM"))
    
    elif data.startswith('cancel_'):
        class_id = data.split('_')[1]
        success, message = cancel_class(class_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

# 定時任務：課前提醒
def send_daily_reminder():
    while True:
        now = datetime.now()
        
        # 每天早上9點發送當日課程提醒
        if now.hour == 9 and now.minute == 0:
            conn = sqlite3.connect('tutor_bot.db')
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    SELECT student_name, start_time, end_time
                    FROM classes 
                    WHERE date(start_time) = date('now')
                    AND status = 'scheduled'
                    ORDER BY start_time
                ''')
                
                classes = cursor.fetchall()
                if classes:
                    message = "早安~\n\n今天有以下的日文家教(依照開始時間由早至晚排序，24小時制)\n"
                    for class_info in classes:
                        start_time = datetime.strptime(class_info[1], '%Y-%m-%d %H:%M:%S')
                        end_time = datetime.strptime(class_info[2], '%Y-%m-%d %H:%M:%S')
                        message += f"{class_info[0]} {start_time.strftime('%Y-%m-%d %H:%M')} {end_time.strftime('%Y-%m-%d %H:%M')}\n"
                    
                    # 這裡需要您的LINE User ID來發送訊息
                    # line_bot_api.push_message('YOUR_USER_ID', TextSendMessage(text=message))
            
            finally:
                conn.close()
        
        time.sleep(60)  # 每分鐘檢查一次

# 啟動定時任務
reminder_thread = threading.Thread(target=send_daily_reminder, daemon=True)
reminder_thread.start()

if __name__ == "__main__":
    init_database()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
