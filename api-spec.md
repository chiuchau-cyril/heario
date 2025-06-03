# Heario API Specification

## Overview

This document describes the API endpoints for the Heario AI-powered news platform. It includes endpoints for fetching news summaries, generating audio and video content, user authentication, preferences, and RSS feed access.

---

## 📘 News Endpoints

### `GET /api/news`

* **Description** : Retrieves a list of summarized news cards.
* **Query Parameters** : None
* **Response Format** :

```json
[
  {
    "id": "string",
    "title": "string",
    "summary": "string",
    "url": "string",
    "created_at": "ISODateTime"
  }
]
```

* **Status** : ✅ Implemented
* **Authentication** : Not required
* **Error Responses** :
* `500 Internal Server Error`

### `GET /api/audio`

* **Description** : Retrieves a TTS audio file for a specific news item.
* **Query Parameters** :
* `id`: News item ID (required)
* **Response** : Audio file (MP3 or OGG)
* **Status** : ⏳ In Progress
* **Authentication** : Not required (may require for premium voice in future)
* **Error Responses** :
* `400 Bad Request` – if** **`id` missing
* `404 Not Found` – if news not found

### `GET /api/video`

* **Description** : Retrieves a video file of a virtual anchor reading a news item.
* **Query Parameters** :
* `id`: News item ID (required)
* **Response** : Video stream (HLS)
* **Status** : 🔜 Planned
* **Authentication** : Required for premium users
* **Error Responses** :
* `401 Unauthorized`
* `404 Not Found`

---

## 🔐 User Endpoints

### `POST /api/user/login`

* **Description** : Authenticates a user using OAuth.
* **Request Body** :

```json
{
  "provider": "string", // e.g., "google", "facebook"
  "token": "string"
}
```

* **Response** :

```json
{
  "user_id": "string",
  "access_token": "string"
}
```

* **Status** : 🔜 Planned
* **Authentication** : Not required
* **Error Responses** :
* `400 Bad Request`
* `401 Unauthorized`

### `POST /api/user/preferences`

* **Description** : Sets a user's news topic preferences.
* **Request Headers** :
* `Authorization: Bearer <token>`
* **Request Body** :

```json
{
  "topics": ["AI", "Finance"]
}
```

* **Response** : 200 OK
* **Status** : 🔜 Planned
* **Authentication** : Required
* **Error Responses** :
* `401 Unauthorized`
* `400 Bad Request`

---

## 📰 RSS Endpoint

### `GET /api/rss`

* **Description** : Returns the podcast RSS feed.
* **Response** : RSS XML
* **Status** : ⏳ In Progress
* **Authentication** : Not required

---

## 🛠 Miscellaneous

### `POST /api/feedback`

* **Description** : Submits feedback or a bug report.
* **Request Body** :

```json
{
  "message": "string",
  "user_id": "string" // optional
}
```

* **Response** : 200 OK
* **Status** : 🔜 Planned
* **Authentication** : Optional
* **Error Responses** :
* `400 Bad Request`

---

## Swagger (OpenAPI) YAML

```yaml
openapi: 3.0.3
info:
  title: Heario API
  version: 1.0.0
paths:
  /api/news:
    get:
      summary: Get summarized news cards
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/NewsCard'
  /api/audio:
    get:
      summary: Get TTS audio file
      parameters:
        - in: query
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Audio stream
        '400':
          description: Missing ID
        '404':
          description: News not found
  /api/video:
    get:
      summary: Get video with virtual anchor
      parameters:
        - in: query
          name: id
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Video stream
        '401':
          description: Unauthorized
        '404':
          description: Not found
components:
  schemas:
    NewsCard:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        summary:
          type: string
        url:
          type: string
        created_at:
          type: string
          format: date-time
```

---

## Notes

* All endpoints use RESTful conventions.
* All requests and responses are JSON unless otherwise specified.
* Authentication should be handled via Bearer token in headers.
* Rate limits and pagination will be added in later releases.
