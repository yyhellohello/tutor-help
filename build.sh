#!/usr/bin/env bash
# exit on error
set -o errexit

# 安裝 Python 依賴
pip install --upgrade pip
pip install -r requirements.txt
