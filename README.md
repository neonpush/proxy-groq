# Groq API Proxy Server

A FastAPI-based proxy server for the Groq API with streaming support.

## Features

- Supports both streaming and non-streaming requests
- Handles Server-Sent Events (SSE) for streaming responses
- Environment-based API key configuration
- Ready for Railway deployment

## Local Development

### Prerequisites

- Python 3.8+
- Groq API key

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your API key:
```bash
export GROQ_API_KEY=your_api_key_here
```

3. Run the server:
```bash
uvicorn groq_proxy:app --reload
```

The server will be available at `http://localhost:8000`

## Railway Deployment

### Deploy with Railway CLI

1. Initialize Railway project:
```bash
railway init
```

2. Set environment variable:
```bash
railway variables --set GROQ_API_KEY=your_api_key_here
```

3. Deploy:
```bash
railway up
```

4. Get your deployment URL:
```bash
railway domain
```

## Usage

### Streaming Request

```bash
curl https://YOUR-RAILWAY-URL.railway.app/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "model": "openai/gpt-oss-120b",
    "temperature": 1,
    "max_completion_tokens": 8192,
    "top_p": 1,
    "stream": true,
    "reasoning_effort": "medium"
  }'
```

### Non-Streaming Request

```bash
curl https://YOUR-RAILWAY-URL.railway.app/ \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello!"
      }
    ],
    "model": "openai/gpt-oss-120b",
    "stream": false
  }'
```

## API Endpoint

### POST `/`

Proxies requests to the Groq API at `https://api.groq.com/openai/v1/chat/completions`

**Request Body**: Same as Groq API chat completions endpoint

**Response**: 
- If `stream: true`: Server-Sent Events stream
- If `stream: false`: JSON response

## Environment Variables

- `GROQ_API_KEY` (required): Your Groq API key
- `PORT` (Railway sets automatically): Server port

## License

MIT

