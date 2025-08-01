#!/usr/bin/env python3
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def clear_news():
    """清除舊的新聞資料"""
    mongo_client = MongoClient(os.getenv('MONGODB_URI'))
    db = mongo_client.heario
    news_collection = db.news
    
    result = news_collection.delete_many({})
    print(f"Deleted {result.deleted_count} news items")

if __name__ == "__main__":
    clear_news()