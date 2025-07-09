# Ollama Bash Agent

This project is an AI agent that:
- Accepts a natural language prompt from the user
- Uses Ollama with the DeepSeek-Coder model to generate Bash one-liners
- Executes the generated Bash command
- Returns the output to the user

## Requirements
- Python 3.8+
- Ollama installed and running (https://ollama.com/download)
- DeepSeek-Coder model pulled: `ollama pull deepseek-coder:1.3b`

## Usage
1. Start Ollama and ensure the DeepSeek-Coder model is available.
2. Run the agent:
   ```bash
   python main.py
   ```
3. Enter your task in plain English. The agent will generate, run, and display the result of the Bash command.

## Security Warning
- This agent will execute generated Bash commands. Review outputs and use in a safe environment.
