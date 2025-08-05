"""
Audio generation routes for TTS functionality
"""

import os
import json
import tempfile
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from services.tts_service import TTSService
import logging

logger = logging.getLogger(__name__)

audio_bp = Blueprint('audio', __name__, url_prefix='/api/audio')

# Initialize TTS service
tts_service = TTSService()

@audio_bp.route('/test', methods=['GET'])
def test_tts():
    """Test TTS functionality"""
    try:
        if tts_service.test_tts():
            return jsonify({
                'status': 'success',
                'message': 'TTS service is working properly'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'TTS service test failed'
            }), 500
    except Exception as e:
        logger.error(f"TTS test error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'TTS test failed: {str(e)}'
        }), 500

@audio_bp.route('/synthesize', methods=['POST'])
def synthesize_text():
    """
    Synthesize a single text to speech
    
    Request JSON:
    {
        "text": "要合成的文字",
        "language": "zh-TW" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing text parameter'
            }), 400
        
        text = data['text']
        language = data.get('language')
        
        if not text.strip():
            return jsonify({
                'status': 'error',
                'message': 'Text cannot be empty'
            }), 400
        
        logger.info(f"Synthesizing text: {text[:50]}...")
        
        # Generate audio
        audio_content = tts_service.synthesize_text(text, language)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Return audio file
        return send_file(
            temp_file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f'tts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3'
        )
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Text synthesis error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'語音合成失敗: {str(e)}'
        }), 500

@audio_bp.route('/generate', methods=['POST'])
def generate_playlist_audio():
    """
    Generate audio for an entire news playlist
    
    Request JSON:
    {
        "playlist": {
            "title": "播放清單標題",
            "items": [
                {
                    "newsItem": {
                        "title": "新聞標題",
                        "summary": "新聞摘要"
                    }
                }
            ]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'playlist' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing playlist parameter'
            }), 400
        
        playlist = data['playlist']
        playlist_title = playlist.get('title', '新聞播放清單')
        playlist_items = playlist.get('items', [])
        
        if not playlist_items:
            return jsonify({
                'status': 'error',
                'message': 'Playlist cannot be empty'
            }), 400
        
        logger.info(f"Generating audio for playlist: {playlist_title} ({len(playlist_items)} items)")
        
        # Generate combined audio
        audio_content = tts_service.create_playlist_audio(playlist_items, playlist_title)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Return audio file
        filename = f'playlist_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3'
        
        return send_file(
            temp_file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Playlist audio generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'播放清單音頻生成失敗: {str(e)}'
        }), 500

@audio_bp.route('/news', methods=['POST'])
def generate_news_audio():
    """
    Generate audio for a single news item
    
    Request JSON:
    {
        "newsItem": {
            "title": "新聞標題",
            "summary": "新聞摘要"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'newsItem' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing newsItem parameter'
            }), 400
        
        news_item = data['newsItem']
        
        logger.info(f"Generating audio for news: {news_item.get('title', 'Unknown')}")
        
        # Generate audio
        audio_content = tts_service.create_news_audio(news_item)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        # Return audio file
        filename = f'news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp3'
        
        return send_file(
            temp_file_path,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=filename
        )
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"News audio generation error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'新聞音頻生成失敗: {str(e)}'
        }), 500

# Legacy endpoint for backward compatibility
@audio_bp.route('/audio', methods=['GET'])
def get_audio():
    """獲取 TTS 音訊檔案 - Legacy endpoint"""
    return jsonify({
        'message': 'Please use /api/audio/generate for playlist audio generation',
        'available_endpoints': [
            'GET /api/audio/test - Test TTS functionality',
            'POST /api/audio/synthesize - Synthesize text to speech',
            'POST /api/audio/generate - Generate playlist audio',
            'POST /api/audio/news - Generate single news audio'
        ]
    })