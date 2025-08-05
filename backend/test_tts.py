#!/usr/bin/env python3
"""
Simple test script for TTS functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.tts_service import TTSService

def test_tts_basic():
    """Test basic TTS functionality"""
    print("🎤 Testing TTS Service...")
    
    try:
        tts = TTSService()
        
        if tts.client is None:
            print("❌ TTS client not initialized (Google Cloud credentials needed)")
            print("\n📋 To set up Google Cloud TTS:")
            print("1. Create a Google Cloud project")
            print("2. Enable the Text-to-Speech API")
            print("3. Create a service account and download JSON key")
            print("4. Set GOOGLE_APPLICATION_CREDENTIALS environment variable")
            print("\nExample:")
            print("export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json")
            return False
        
        # Test basic functionality
        print("✅ TTS client initialized successfully")
        
        # Test text synthesis
        test_text = "這是一個測試。這個系統可以將文字轉換成語音。"
        print(f"🔊 Testing synthesis with: {test_text}")
        
        audio_content = tts.synthesize_text(test_text)
        print(f"✅ Synthesis successful! Generated {len(audio_content)} bytes of audio")
        
        # Test language detection
        chinese_text = "這是中文測試"
        english_text = "This is an English test"
        
        print(f"🌐 Chinese text detected as: {tts.detect_language(chinese_text)}")
        print(f"🌐 English text detected as: {tts.detect_language(english_text)}")
        
        # Test news audio creation
        test_news = {
            'title': '測試新聞標題',
            'summary': '這是一個測試新聞的摘要內容，用來測試TTS系統是否能正常運作。'
        }
        
        print("📰 Testing news audio creation...")
        news_audio = tts.create_news_audio(test_news)
        print(f"✅ News audio created! Generated {len(news_audio)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_tts_basic()
    if success:
        print("\n🎉 TTS service is ready!")
    else:
        print("\n⚠️  TTS service needs setup")
    
    sys.exit(0 if success else 1)