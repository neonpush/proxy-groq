from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

logger.info("✅ Groq Proxy Server started successfully")
logger.info(f"✅ API Key loaded: {GROQ_API_KEY[:10]}...")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Server startup complete - endpoints registered")
    logger.info("📍 Available endpoints: POST /, POST /chat/completions")

async def proxy_handler(req: Request):
    """Handle proxy requests to Groq API"""
    logger.info(f"📥 Received request to {req.url.path}")
    
    try:
        data = await req.json()
        logger.info(f"📦 Request data: model={data.get('model')}, stream={data.get('stream')}, messages={len(data.get('messages', []))} messages")
        
        async with httpx.AsyncClient() as client:
            # Check if streaming is requested
            is_streaming = data.get("stream", False)
            
            if is_streaming:
                logger.info("🌊 Handling streaming request")
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
                        logger.info(f"✅ Groq API response status: {response.status_code}")
                        async for chunk in response.aiter_bytes():
                            yield chunk
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream"
                )
            else:
                logger.info("📄 Handling non-streaming request")
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
                logger.info(f"✅ Groq API response status: {r.status_code}")
                return r.json()
    except Exception as e:
        logger.error(f"❌ Error processing request: {str(e)}")
        raise

# Support both root and /chat/completions endpoints
@app.post("/")
async def proxy_root(req: Request):
    logger.info("🔗 Root endpoint (/) called")
    return await proxy_handler(req)

@app.post("/chat/completions")
async def proxy_chat_completions(req: Request):
    logger.info("🔗 /chat/completions endpoint called")
    return await proxy_handler(req)

