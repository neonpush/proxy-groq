from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import httpx
import os

# Load .env file for local development
load_dotenv()

app = FastAPI()

# Get API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. "
        "Please set it in your Railway dashboard: "
        "Settings > Variables > Add Variable"
    )

async def proxy_handler(req: Request):
    """Handle proxy requests to Groq API"""
    data = await req.json()
    
    async with httpx.AsyncClient() as client:
        # Check if streaming is requested
        is_streaming = data.get("stream", False)
        
        if is_streaming:
            # Handle streaming response
            async def stream_generator():
                async with client.stream(
                    "POST",
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=data,
                    timeout=60.0
                ) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream"
            )
        else:
            # Handle non-streaming response
            r = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=60.0
            )
            return r.json()

# Support both root and /chat/completions endpoints
@app.post("/")
async def proxy_root(req: Request):
    return await proxy_handler(req)

@app.post("/chat/completions")
async def proxy_chat_completions(req: Request):
    return await proxy_handler(req)

