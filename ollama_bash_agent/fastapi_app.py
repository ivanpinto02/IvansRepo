from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import platform
import re
import json
from typing import Dict, Any

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
AVAILABLE_MODELS = ["llama3", "deepseek-coder:1.3b"]

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Add custom template globals
templates.env.globals.update({
    'get_flashed_messages': lambda: []  # Empty list since we're not using Flask's flash messages
})

# --- Command Extraction Logic (ported from Flask version) ---
def extract_command(text):
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    cleaned = [l for l in lines if not l.startswith('```') and not l.lower().startswith('you should') and not l.lower().startswith('run this') and not l.lower().startswith('to')]
    for l in cleaned:
        if re.match(r'^[\w\-\.]+[\w\s\-\.\/\\:\u003e\u003c\"\'=]*$', l) and not l.startswith('#'):
            return l
    if cleaned:
        return cleaned[0]
    elif lines:
        return lines[0]
    else:
        return text.strip()

async def prompt_ollama(prompt, model):
    system = platform.system()
    shell_type = "Windows cmd" if system == "Windows" else "bash"
    data = {
        "model": model,
        "prompt": (
            f"You are a helpful assistant that generates {shell_type} commands. "
            f"For the following request, provide a single, well-documented command.\n"
            f"Request: {prompt}\n\n"
            f"Respond with a JSON object containing two fields: 'command' and 'explanation'. "
            f"The 'explanation' should clearly describe what the command does. "
            f"Example: {{\"command\": \"ls -la\", \"explanation\": \"List all files in the current directory in long format\"}}"
        ),
        "stream": False,  # Disable streaming from Ollama to get complete responses
        "format": "json"   # Request JSON format explicitly
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:  # Add a reasonable timeout
            response = await client.post(OLLAMA_API_URL, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            try:
                result = response.json()
                if 'response' in result:
                    # Try to parse the response as JSON
                    try:
                        command_data = json.loads(result['response'])
                        if isinstance(command_data, dict) and 'command' in command_data:
                            # Format the output with command and explanation
                            output = f"Command:\n{command_data['command']}\n\n"
                            if 'explanation' in command_data:
                                output += f"Explanation:\n{command_data['explanation']}"
                            yield output
                            return
                    except json.JSONDecodeError:
                        # If not JSON, just return the raw response
                        yield result['response']
                else:
                    yield "Error: Unexpected response format from the model"
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                yield "Error: Could not parse the model's response"
                
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e}")
        yield f"Error: Could not connect to the Ollama API. Status code: {e.response.status_code}"
    except httpx.RequestError as e:
        print(f"Request error: {e}")
        yield "Error: Could not connect to the Ollama service. Please make sure it's running."
    except Exception as e:
        print(f"Unexpected error: {e}")
        yield "An unexpected error occurred while processing your request."

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    injected_data = {
        "prompt": None,
        "model": DEFAULT_MODEL,
        "bash_command": None,
        "output": None,
        "error": None,
        "raw_model_output": None,
        "history": [],
    }
    return templates.TemplateResponse("index.html", {
        "request": request,
        "injected_data": injected_data,
        "models": AVAILABLE_MODELS
    })

@app.post("/", response_class=HTMLResponse)
async def index_post(request: Request, prompt: str = Form(...), model: str = Form(...)):
    # TODO: Integrate your async LLM logic here. For now, just echo the prompt/model.
    injected_json = json.dumps({
        "prompt": prompt,
        "model": model,
        "bash_command": f"Generated for: {prompt}",
        "output": None,
        "error": None,
        "raw_model_output": None,
        "history": [],
    })
    return templates.TemplateResponse("index.html", {
        "request": request,
        "injected_json": injected_json,
        "models": AVAILABLE_MODELS
    })

@app.get("/stream")
async def stream(
    request: Request,
    prompt: str,
    model: str = DEFAULT_MODEL,
    _: str = ""  # Cache-busting parameter from the client
):
    """Stream responses from Ollama using Server-Sent Events (SSE)."""
    
    async def send_sse_message(event_type: str, data: str, event_id: str = None, retry: int = None) -> str:
        """Format a message according to the SSE specification."""
        message = []
        if event_type:
            message.append(f"event: {event_type}")
        if data is not None:
            # Ensure data is properly escaped for SSE
            data = data.replace('\n', '\\n').replace('\r', '\\r')
            message.append(f"data: {data}")
        if event_id:
            message.append(f"id: {event_id}")
        if retry is not None:
            message.append(f"retry: {retry}")
        message.append("\n")  # End with a blank line
        return "\n".join(message)
    
    async def event_generator():
        try:
            print(f"Starting stream for prompt: {prompt[:50]}...")
            
            # Send an initial status message
            yield await send_sse_message(
                event_type="status",
                data="Connected to the server. Processing your request...",
                event_id=str(uuid.uuid4())
            )
            
            # Flush the buffer to ensure the client receives the initial message
            await asyncio.sleep(0.1)
            
            # Process the prompt with Ollama
            async for chunk in prompt_ollama(prompt, model):
                if await request.is_disconnected():
                    print("Client disconnected")
                    break
                
                if not chunk or not chunk.strip():
                    continue
                
                try:
                    # Clean and format the chunk
                    clean_chunk = chunk.strip()
                    
                    # Send the chunk as a message event
                    yield await send_sse_message(
                        event_type="message",
                        data=clean_chunk,
                        event_id=str(uuid.uuid4())
                    )
                    
                    # Small delay to prevent overwhelming the client
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    error_msg = f"Error processing response: {str(e)}"
                    print(error_msg)
                    yield await send_sse_message(
                        event_type="error",
                        data=error_msg,
                        event_id=str(uuid.uuid4())
                    )
                    continue
                        
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            yield await send_sse_message(
                event_type="error",
                data=error_msg,
                retry=5000  # Suggest client to retry after 5 seconds
            )
            
        finally:
            # Send an end-of-stream marker
            yield await send_sse_message(
                event_type="end",
                data="\n\n--- Stream ended ---",
                event_id=str(uuid.uuid4())
            )
            print("Stream ended")
    
    # Configure response headers for SSE
    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream; charset=utf-8",
        "X-Accel-Buffering": "no",  # Disable buffering in Nginx if used
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    # Add CORS preflight support
    if request.method == "OPTIONS":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"message": "OK"},
            headers=headers
        )
    
    # Configure the SSE response
    response = EventSourceResponse(
        event_generator(),
        headers=headers,
        ping=15,  # Send a ping every 15 seconds to keep the connection alive
        ping_message_factory=lambda: {"event": "ping", "data": ""}
    )
    
    return response
