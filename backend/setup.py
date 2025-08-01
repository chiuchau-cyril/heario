#!/usr/bin/env python3
import os
import shutil

def setup_environment():
    """設定環境變數檔案"""
    if not os.path.exists('.env'):
        shutil.copy('.env.example', '.env')
        print("已建立 .env 檔案，請填入你的 API keys")
    else:
        print(".env 檔案已存在")

if __name__ == "__main__":
    setup_environment()