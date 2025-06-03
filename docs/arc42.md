# arc42 Software Architecture Documentation – Heario

# 1. Introduction and Goals

## 1.1 Requirements Overview

Heario is an AI-powered personal news broadcasting platform designed to automatically fetch, summarize, vocalize, and visualize news. It aims to support commuting users with a customizable, intuitive experience.

## 1.2 Quality Goals

* Easy-to-use interface for non-technical users
* Modular architecture for phased development
* Scalable backend for handling news ingestion, summarization, TTS, and video generation
* Low-latency audio and video streaming

## 1.3 Stakeholders

* End users (commuters, podcast listeners)
* Developer (solo)
* Potential future advertisers and subscription customers

# 2. Architecture Constraints

* Frontend: React or Vue.js
* Backend: Flask or Django
* TTS: Whisper API or edge-tts
* Streaming: WebRTC + Cloudflare Stream
* Hosting: Cloud Run, Vercel, Render

# 3. System Scope and Context

## 3.1 Business Context

Heario targets users who prefer listening to news during their morning routine or commute. It provides an automated solution combining AI summarization, TTS, and virtual anchors.

## 3.2 Technical Context

* Frontend connects to backend via RESTful APIs
* Backend manages data flow between crawler, summarizer, TTS, and video modules
* External APIs: Google News, Jina.ai, OpenAI GPT, Whisper

# 4. Solution Strategy

* Start with MVP: Card-based news summarization
* Layer in TTS podcast functionality
* Expand to animated virtual anchor videos
* Ensure modularity for plug-and-play components (e.g., TTS, LipSync, streaming)

# 5. Building Block View

## 5.1 Whitebox Overview

* Frontend: NewsCardApp (UI)
* Backend: Flask/Django
  * /api/news
  * /api/audio
  * /api/video
* Storage: MongoDB or MySQL
* Modules:
  * Crawler: Google News via Jina.ai
  * LLM Summarizer: OpenAI GPT
  * TTS: Whisper API
  * Video Gen: LipSync + Animate/Unity

## 5.2 Level 2 Decomposition

* Frontend
  * NewsCard component
  * AudioPlayer component
  * Login/ThemeSelector (Phase 2+)
* Backend
  * news_controller.py
  * tts_controller.py
  * video_controller.py
  * rss_generator.py

# 6. Runtime View

* Crawler fetches articles → LLM summarizes → Data stored in DB
* User accesses frontend → frontend fetches /api/news → displays cards
* On click play: /api/audio returns audio file → streamed via Cloudflare
* Video gen is async and delivered via /api/video endpoint (Phase 3)

# 7. Deployment View

* Frontend deployed via Vercel (React or Vue)
* Backend deployed via Cloud Run / Render
* Database managed on hosted MongoDB / MySQL (e.g., PlanetScale)
* Audio/Video files stored and streamed from Cloudflare Stream

# 8. Cross-cutting Concepts

* Authentication: OAuth (Firebase Auth/Supabase)
* API Format: REST + JSON
* Audio: mp3/ogg, Video: HLS/WebRTC
* Logging: Simple file-based logging + Cloud monitoring

# 9. Design Decisions

* Chose GPT over custom summarization for quality and speed
* Modular TTS to support future switch to ElevenLabs
* React preferred for better ecosystem support

# 10. Quality Requirements

* Usability: Minimal onboarding
* Performance: Audio within 1s delay, video within 5s post-generation
* Scalability: Handle spikes in traffic with serverless backend

# 11. Risks and Technical Debt

* LipSync quality remains unknown
* Cloudflare Stream cost scaling
* News source legal compliance

# 12. Glossary

* LLM: Large Language Model
* TTS: Text-to-Speech
* HLS: HTTP Live Streaming
* WebRTC: Web Real-Time Communication
* MVP: Minimum Viable Product
