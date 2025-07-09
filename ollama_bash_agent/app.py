import os
import platform
import requests
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file

OLLAMA_API_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"
AVAILABLE_MODELS = ["llama3", "deepseek-coder:1.3b"]

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flash messages
app.config['SESSION_TYPE'] = 'filesystem'

import re
import json

def extract_command(text):
    # Remove code block markers and instructions
    lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
    cleaned = [l for l in lines if not l.startswith('```') and not l.lower().startswith('you should') and not l.lower().startswith('run this') and not l.lower().startswith('to')]
    # Use regex to find the first plausible command (line with typical shell/cmd syntax)
    for l in cleaned:
        # Match a line that looks like a command (starts with a word character, not a comment, not empty)
        if re.match(r'^[\w\-\.]+[\w\s\-\.\/\\:><|\"\'=]*$', l) and not l.startswith('#'):
            return l
    # Fallback to first cleaned line
    if cleaned:
        return cleaned[0]
    elif lines:
        return lines[0]
    else:
        return text.strip()

def extract_json(text):
    # Remove code block markers and clean up output
    cleaned = text.replace('```json', '').replace('```', '').replace("'", '"').replace('\\', '\\').strip()
    # Try to fix common LLM JSON issues: missing brackets, trailing commas
    # Add opening bracket if missing and output looks like a list of dicts
    if not cleaned.startswith('[') and cleaned.lstrip().startswith('{'):
        cleaned = '[' + cleaned
    # Add closing bracket if missing
    if cleaned.startswith('[') and not cleaned.rstrip().endswith(']'):
        cleaned = cleaned.rstrip(',\n ') + ']'
    # Remove trailing comma before closing bracket
    cleaned = re.sub(r',\s*\]$', ']', cleaned)
    # Try JSON array of steps first
    if cleaned.startswith('['):
        try:
            arr = json.loads(cleaned)
            if isinstance(arr, list) and all(isinstance(step, dict) and 'command' in step for step in arr):
                return arr
        except Exception as e:
            # Try to extract the longest valid array substring
            array_match = re.search(r'\[.*', cleaned, re.DOTALL)
            if array_match:
                raw_array = array_match.group()
                if raw_array.count('[') > raw_array.count(']'):
                    raw_array += ']'
                try:
                    arr = json.loads(raw_array)
                    if isinstance(arr, list) and all(isinstance(step, dict) and 'command' in step for step in arr):
                        return arr
                except Exception as e2:
                    print(f"[WARN] JSON array decode error (auto-close): {e2}\nRaw: {raw_array}")
            print(f"[WARN] JSON array decode error: {e}\nRaw: {cleaned}")
    # Fallback: single JSON object
    json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if json_match:
        raw_json = json_match.group()
        try:
            json_obj = json.loads(raw_json)
            if 'command' in json_obj and isinstance(json_obj['command'], str):
                return json_obj['command'].strip()
        except Exception as e:
            print(f"[WARN] JSON decode error: {e}\nRaw JSON: {raw_json}")
    print(f"[ERROR] Could not extract valid JSON. Raw output: {text}")
    return None

def prompt_ollama(prompt, model):
    system = platform.system()
    if system == "Windows":
        shell_type = "Windows cmd"
    else:
        shell_type = "bash"
    # Ask for JSON array of steps
    data = {
        "model": model,
        "prompt": (
            f"Respond ONLY with a JSON array. Each element should be an object with keys 'command' and 'explanation'. "
            f"The 'explanation' must be a clear, natural language description of what the command does, and must never be left blank. "
            f"Do not include any text outside the JSON array. Each command should be a {shell_type} one-liner.\n"
            f"Steps: {prompt}"
        )
    }
    response = requests.post(OLLAMA_API_URL, json=data, stream=True)
    command = ""
    for line in response.iter_lines():
        if not line:
            continue
        try:
            payload = json.loads(line.decode("utf-8"))
            if 'response' in payload:
                command += payload['response']
        except Exception:
            continue
    json_command = extract_json(command)
    error = None
    if json_command is not None:
        return json_command, command, error
    # Fallback: scan all lines for plausible command
    known_cmds = r'^(echo|dir|start|type|cd|copy|move|del|cls|ls|pwd|cat|touch|rm|cp|mv|whoami|hostname|date|time|exit|shutdown|ipconfig|ifconfig|tree|findstr|grep|curl|wget|python|pip|powershell|cmd|set|env)'
    for line in command.splitlines():
        l = line.strip()
        if re.match(known_cmds, l, re.IGNORECASE):
            error = "Used fallback extraction."
            return l, command, error
    error = "Could not extract any plausible command."
    return "echo ERROR: Could not extract command from model output", command, error

def run_command(command):
    try:
        result = os.popen(command).read()
        return result
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    bash_command = ''
    error = None
    raw_model_output = None
    approved = False
    steps = None
    model = request.form.get('model') or session.get('selected_model') or DEFAULT_MODEL
    if request.method == 'POST':
        user_prompt = request.form.get('prompt')
        approve = request.form.get('approve')
        if user_prompt:
            session['pending_prompt'] = user_prompt
            session['selected_model'] = model
            # Generate command or steps but do not run yet
            cmd, raw_model_output, error = prompt_ollama(user_prompt, model)
            # If multi-step, store steps
            if isinstance(cmd, list):
                session['pending_steps'] = cmd
                session['pending_command'] = None
            else:
                session['pending_command'] = cmd
                session['pending_steps'] = None
            session['pending_raw'] = raw_model_output
            session['pending_error'] = error
            return render_template('index.html', bash_command=cmd if not isinstance(cmd, list) else None, steps=cmd if isinstance(cmd, list) else None, output=None, error=error, raw_model_output=raw_model_output, approved=False, prompt=user_prompt, model=model, models=AVAILABLE_MODELS, history=session.get('history', []))
        elif approve:
            # User approved the command or steps, so run it/them
            steps = session.get('pending_steps', None)
            if steps:
                # Run all steps and collect outputs
                outputs = []
                for step in steps:
                    o = run_command(step['command'])
                    outputs.append({'command': step['command'], 'explanation': step.get('explanation',''), 'output': o})
                output = outputs
                bash_command = None
            else:
                bash_command = session.get('pending_command', '')
                output = run_command(bash_command)
            user_prompt = session.get('pending_prompt', '')
            raw_model_output = session.get('pending_raw', '')
            error = session.get('pending_error', None)
            # Save to history
            entry = {'prompt': user_prompt, 'command': bash_command if bash_command else steps, 'output': output, 'model': model}
            history = session.get('history', [])
            history.append(deepcopy(entry))
            session['history'] = history[-10:]  # Keep last 10
            # Clear pending
            session.pop('pending_command', None)
            session.pop('pending_steps', None)
            session.pop('pending_prompt', None)
            session.pop('pending_raw', None)
            session.pop('pending_error', None)
            approved = True
            return render_template('index.html', bash_command=bash_command, steps=steps, output=output, error=error, raw_model_output=raw_model_output, approved=approved, prompt=user_prompt, model=model, models=AVAILABLE_MODELS, history=history)
    # GET or fallback
    return render_template('index.html', bash_command=None, steps=None, output=None, error=None, raw_model_output=None, approved=False, prompt=None, model=model, models=AVAILABLE_MODELS, history=session.get('history', []))

from io import BytesIO

@app.route('/download', methods=['POST'])
def download_output():
    output = request.form.get('output', '')
    mem = BytesIO()
    mem.write(output.encode('utf-8'))
    mem.seek(0)
    return send_file(mem, as_attachment=True, download_name='output.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
