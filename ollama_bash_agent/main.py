import subprocess
import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "deepseek-coder:1.3b"

import platform

def prompt_ollama(prompt):
    system = platform.system()
    if system == "Windows":
        shell_type = "Windows cmd"
    else:
        shell_type = "bash"
    data = {
        "model": OLLAMA_MODEL,
        "prompt": f"Write a {shell_type} one-liner for: {prompt}\nJust output the code, nothing else."
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
    # Strip code block markers if present
    lines = [l.strip() for l in command.strip().split('\n') if l.strip()]
    # Remove triple backtick lines and language markers
    cleaned = [l for l in lines if not l.startswith('```')]
    if cleaned:
        return cleaned[0]
    elif lines:
        return lines[0]
    else:
        return command.strip()

def run_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

import sys

def main():
    print("Ollama Bash Agent (DeepSeek-Coder)")
    # If a prompt is given as a command-line argument, use it directly
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        print(f"[Prompt]: {user_input}")
        print("[Generating Bash command...]")
        bash_command = prompt_ollama(user_input)
        print(f"[Bash command]: {bash_command}")
        print("[Running...]")
        output = run_bash_command(bash_command)
        print(f"[Output]:\n{output}")
        return
    # Otherwise, fall back to interactive mode
    print("Type your task in plain English (or 'exit' to quit):")
    while True:
        try:
            user_input = input("$ ")
        except EOFError:
            print("[EOF received, exiting]")
            break
        if user_input.lower() in ("exit", "quit"):
            break
        print("[Generating Bash command...]")
        bash_command = prompt_ollama(user_input)
        print(f"[Bash command]: {bash_command}")
        print("[Running...]")
        output = run_bash_command(bash_command)
        print(f"[Output]:\n{output}")

if __name__ == "__main__":
    main()
