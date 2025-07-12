from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
import httpx
import platform
import re
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
AVAILABLE_MODELS = ["llama3", "deepseek-coder:1.3b"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
            f"Respond ONLY with a JSON array. Each element should be an object with keys 'command' and 'explanation'. "
            f"The 'explanation' must be a clear, natural language description of what the command does, and must never be left blank. "
            f"Do not include any text outside the JSON array. Each command should be a {shell_type} one-liner.\n"
            f"Prompt: {prompt}"
        )
    }
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("POST", OLLAMA_API_URL, json=data) as response:
            command = ""
            async for line in response.aiter_lines():
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                    if 'response' in payload:
                        command += payload['response']
                        yield command
                except Exception:
                    continue

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    injected_json = json.dumps({
        "prompt": None,
        "model": DEFAULT_MODEL,
        "bash_command": None,
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
async def stream(prompt: str, model: str = DEFAULT_MODEL):
    async def event_generator():
        async for chunk in prompt_ollama(prompt, model):
            yield {"data": chunk}
    return EventSourceResponse(event_generator())
