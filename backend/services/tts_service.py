"""
Text-to-Speech service using Google Cloud TTS
Handles conversion of news playlist to audio files
"""

import os
import json
import tempfile
from typing import List, Dict, Any, Optional
from google.cloud import texttospeech
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        """Initialize Google Cloud TTS client"""
        try:
            # Set the project ID explicitly
            os.environ['GOOGLE_CLOUD_PROJECT'] = 'heario-4099f'
            
            # Initialize the TTS client with explicit project
            from google.cloud import texttospeech
            self.client = texttospeech.TextToSpeechClient()
            self.project_id = 'heario-4099f'
            
            logger.info(f"Google Cloud TTS client initialized successfully for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize TTS client: {e}")
            self.client = None
            self.project_id = None

    def detect_language(self, text: str) -> str:
        """
        Simple language detection for Chinese vs English
        Returns 'zh-TW' for Chinese, 'en-US' for English
        """
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        total_chars = len([c for c in text if c.isalnum()])
        
        if total_chars == 0:
            return 'zh-TW'  # Default to Chinese
        
        chinese_ratio = chinese_chars / total_chars
        return 'zh-TW' if chinese_ratio > 0.3 else 'en-US'

    def get_voice_config(self, language_code: str) -> Dict[str, Any]:
        """
        Get voice configuration for different languages
        """
        voice_configs = {
            'zh-TW': {
                'language_code': 'cmn-TW',
                'name': 'cmn-TW-Standard-A',  # Female voice
                'ssml_gender': texttospeech.SsmlVoiceGender.FEMALE
            },
            'en-US': {
                'language_code': 'en-US',
                'name': 'en-US-Standard-C',  # Female voice
                'ssml_gender': texttospeech.SsmlVoiceGender.FEMALE
            }
        }
        
        return voice_configs.get(language_code, voice_configs['zh-TW'])

    def synthesize_text(self, text: str, language_code: Optional[str] = None) -> bytes:
        """
        Convert text to speech using Google Cloud TTS
        
        Args:
            text: Text to synthesize
            language_code: Language code (auto-detected if None)
            
        Returns:
            Audio content as bytes
        """
        if not self.client:
            raise Exception("TTS client not initialized")
        
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Auto-detect language if not provided
        if not language_code:
            language_code = self.detect_language(text)
        
        logger.info(f"Synthesizing text with language: {language_code}")
        
        # Get voice configuration
        voice_config = self.get_voice_config(language_code)
        
        # Set up synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Set up voice selection
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name'],
            ssml_gender=voice_config['ssml_gender']
        )
        
        # Set up audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal speed
            pitch=0.0,  # Normal pitch
            volume_gain_db=0.0  # Normal volume
        )
        
        try:
            # Perform TTS request with explicit project
            response = self.client.synthesize_speech(
                request={
                    "input": synthesis_input,
                    "voice": voice,
                    "audio_config": audio_config
                },
                timeout=30
            )
            
            logger.info(f"Successfully synthesized {len(response.audio_content)} bytes of audio")
            return response.audio_content
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise Exception(f"語音合成失敗: {str(e)}")

    def create_news_audio(self, news_item: Dict[str, Any]) -> bytes:
        """
        Create audio for a single news item
        
        Args:
            news_item: News item with title and summary
            
        Returns:
            Audio content as bytes
        """
        title = news_item.get('title', '')
        summary = news_item.get('summary', '')
        
        if not title and not summary:
            raise ValueError("News item must have title or summary")
        
        # Create a formatted script for the news
        script_parts = []
        
        if title:
            script_parts.append(f"新聞標題：{title}")
        
        if summary:
            script_parts.append(f"內容摘要：{summary}")
        
        script = "。".join(script_parts) + "。"
        
        logger.info(f"Creating audio for news: {title[:50]}...")
        
        return self.synthesize_text(script)

    def create_playlist_audio(self, playlist_items: List[Dict[str, Any]], 
                            playlist_title: str = "新聞播放清單") -> bytes:
        """
        Create combined audio for an entire playlist
        
        Args:
            playlist_items: List of news items
            playlist_title: Title of the playlist
            
        Returns:
            Combined audio content as bytes
        """
        if not playlist_items:
            raise ValueError("Playlist cannot be empty")
        
        logger.info(f"Creating playlist audio with {len(playlist_items)} items")
        
        audio_segments = []
        
        try:
            # Create intro
            intro_text = f"歡迎收聽{playlist_title}，共有{len(playlist_items)}則新聞。"
            intro_audio = self.synthesize_text(intro_text)
            intro_segment = AudioSegment.from_mp3(io.BytesIO(intro_audio))
            audio_segments.append(intro_segment)
            
            # Add a brief pause after intro
            pause = AudioSegment.silent(duration=1000)  # 1 second pause
            audio_segments.append(pause)
            
            # Process each news item
            for i, item in enumerate(playlist_items, 1):
                try:
                    # Add news number announcement
                    news_intro = f"第{i}則新聞。"
                    news_intro_audio = self.synthesize_text(news_intro)
                    news_intro_segment = AudioSegment.from_mp3(io.BytesIO(news_intro_audio))
                    audio_segments.append(news_intro_segment)
                    
                    # Add brief pause
                    audio_segments.append(AudioSegment.silent(duration=500))
                    
                    # Add news content
                    news_audio = self.create_news_audio(item['newsItem'])
                    news_segment = AudioSegment.from_mp3(io.BytesIO(news_audio))
                    audio_segments.append(news_segment)
                    
                    # Add pause between news items (except last one)
                    if i < len(playlist_items):
                        audio_segments.append(AudioSegment.silent(duration=1500))  # 1.5 second pause
                    
                except Exception as e:
                    logger.error(f"Failed to process news item {i}: {e}")
                    # Continue with next item instead of failing entirely
                    continue
            
            # Create outro
            outro_text = f"新聞播報結束，感謝收聽。"
            outro_audio = self.synthesize_text(outro_text)
            outro_segment = AudioSegment.from_mp3(io.BytesIO(outro_audio))
            audio_segments.append(AudioSegment.silent(duration=1000))
            audio_segments.append(outro_segment)
            
            # Combine all segments
            logger.info("Combining audio segments...")
            combined_audio = sum(audio_segments)
            
            # Export to MP3 bytes
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                combined_audio.export(temp_file.name, format="mp3", bitrate="128k")
                
                with open(temp_file.name, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up temp file
                os.unlink(temp_file.name)
            
            logger.info(f"Successfully created playlist audio: {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Failed to create playlist audio: {e}")
            raise Exception(f"播放清單音頻生成失敗: {str(e)}")

    def test_tts(self) -> bool:
        """
        Test TTS functionality
        
        Returns:
            True if TTS is working, False otherwise
        """
        try:
            if not self.client:
                raise Exception("TTS client not initialized. Please check Google Cloud credentials.")
            
            test_text = "這是一個測試。This is a test."
            audio_content = self.synthesize_text(test_text)
            return len(audio_content) > 0
        except Exception as e:
            logger.error(f"TTS test failed: {e}")
            return False


# Import io for BytesIO
import io