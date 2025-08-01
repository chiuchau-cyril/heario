from flask import Blueprint, jsonify, request

audio_bp = Blueprint('audio', __name__)

@audio_bp.route('/audio', methods=['GET'])
def get_audio():
    """獲取 TTS 音訊檔案"""
    news_id = request.args.get('id')
    
    if not news_id:
        return jsonify({'error': 'Missing news ID'}), 400
    
    return jsonify({'message': 'Audio endpoint - Phase 2 (In Progress)'}), 501