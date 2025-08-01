from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

from routes.news import news_bp
from routes.audio import audio_bp
from routes.rss import rss_bp

load_dotenv()

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3003'], supports_credentials=True)

mongo_client = MongoClient(os.getenv('MONGODB_URI'))
db = mongo_client.heario
app.config['db'] = db

app.register_blueprint(news_bp, url_prefix='/api')
app.register_blueprint(audio_bp, url_prefix='/api')
app.register_blueprint(rss_bp, url_prefix='/api')

@app.route('/')
def index():
    return jsonify({
        'message': 'Heario API',
        'version': '1.0.0',
        'endpoints': [
            '/api/news',
            '/api/audio',
            '/api/rss'
        ]
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)