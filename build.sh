#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝系統依賴
apt-get update
apt-get install -y build-essential python3-dev

# 安裝 Python 依賴
pip install --upgrade pip
pip install -r requirements.txt
