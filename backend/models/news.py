from datetime import datetime
from bson import ObjectId

class NewsItem:
    def __init__(self, title, summary, url, source=None, original_content=None):
        self.title = title
        self.summary = summary
        self.url = url
        self.source = source
        self.original_content = original_content
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'title': self.title,
            'summary': self.summary,
            'url': self.url,
            'source': self.source,
            'original_content': self.original_content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        news = NewsItem(
            title=data.get('title'),
            summary=data.get('summary'),
            url=data.get('url'),
            source=data.get('source'),
            original_content=data.get('original_content')
        )
        if 'created_at' in data:
            news.created_at = data['created_at']
        if 'updated_at' in data:
            news.updated_at = data['updated_at']
        return news
    
    @staticmethod
    def serialize_for_api(news_doc):
        return {
            'id': str(news_doc['_id']),
            'title': news_doc['title'],
            'summary': news_doc['summary'],
            'url': news_doc['url'],
            'created_at': news_doc['created_at'].isoformat() if news_doc.get('created_at') else None
        }