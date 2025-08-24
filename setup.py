#!/usr/bin/env python3
"""
日文家教管理LINE Bot 快速設定腳本
"""

import os
import sys
import subprocess

def install_requirements():
    """安裝必要的套件"""
    print("📦 安裝必要的Python套件...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 套件安裝完成！")
    except subprocess.CalledProcessError:
        print("❌ 套件安裝失敗，請手動執行：pip install -r requirements.txt")
        return False
    return True

def init_database():
    """初始化資料庫"""
    print("🗄️ 初始化資料庫...")
    try:
        from app import init_database
        init_database()
        print("✅ 資料庫初始化完成！")
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        return False
    return True

def test_connections():
    """測試各種連接"""
    print("🔗 測試連接...")
    try:
        subprocess.check_call([sys.executable, "test_bot.py"])
        print("✅ 連接測試完成！")
    except subprocess.CalledProcessError:
        print("❌ 連接測試失敗，請檢查設定")
        return False
    return True

def create_env_file():
    """建立環境變數檔案範例"""
    print("📝 建立環境變數檔案...")
    env_content = """# LINE Bot 設定
LINE_CHANNEL_SECRET=d2be7216d3a0cf571c96f45b23dfc01d
LINE_CHANNEL_ACCESS_TOKEN=9J4cAf8zpSxPDKSoZbgTrGXTEeCEVVkvuUwBrqZ9Vo5hmcFgM5EaE0ouGfXsZy5DEsyEDi1FpfqzwYMZfDeyEj//CbgVIj42iMCa6N5VtMVSt2ev3cSNWnSRmvIJExo5S6f61tYPmZdJ5CEs3loprwdB04t89/1O/w1cDnyilFU=

# Google API 設定
CALENDAR_ID=forget775981@gmail.com
DRIVE_ROOT_FOLDER_ID=1--LlRPbaE0vbo62N__kI_5VqnfRbWCpH

# 部署設定
PORT=5000
"""
    
    with open('.env.example', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 環境變數檔案範例已建立 (.env.example)")

def main():
    """主設定函數"""
    print("🚀 日文家教管理LINE Bot 快速設定")
    print("=" * 50)
    
    # 檢查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    # 安裝套件
    if not install_requirements():
        return
    
    # 初始化資料庫
    if not init_database():
        return
    
    # 建立環境變數檔案
    create_env_file()
    
    # 測試連接
    if not test_connections():
        return
    
    print("\n" + "=" * 50)
    print("🎉 設定完成！")
    print("\n📋 下一步操作：")
    print("1. 將程式碼上傳到 GitHub:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/yyhellohello/japanese-tutor-bot.git")
    print("   git push -u origin main")
    print("\n2. 在 Railway 部署:")
    print("   - 前往 https://railway.app")
    print("   - 連接 GitHub Repository")
    print("   - 設定環境變數")
    print("   - 部署應用程式")
    print("\n3. 設定 LINE Bot Webhook:")
    print("   - 前往 LINE Developers Console")
    print("   - 設定 Webhook URL")
    print("\n4. 開始使用！")
    print("\n📖 詳細說明請參考 DEPLOYMENT.md")

if __name__ == "__main__":
    main()
