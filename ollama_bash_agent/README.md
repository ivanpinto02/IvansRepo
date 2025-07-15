# Ollama Bash Agent

A web-based AI assistant that generates and explains Bash commands using Ollama's language models. The application features a responsive web interface with real-time streaming of command generation and execution results.

## Features

- **Web Interface**: Modern, responsive UI for interacting with the agent
- **Real-time Streaming**: Uses Server-Sent Events (SSE) for live updates
- **Multiple Models**: Supports various Ollama models (default: llama3)
- **Command Explanation**: Provides detailed explanations for generated commands
- **Safe Execution**: Commands are shown first for review before execution

## Requirements

- Python 3.8+
- Ollama installed and running (https://ollama.com/download)
- Recommended model: `ollama pull llama3`
- Additional Python packages (install via `pip install -r requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ollama-bash-agent
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the Ollama server (if not already running):
   ```bash
   ollama serve
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn fastapi_app:app --reload
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

3. Enter your task in plain English and click "Generate Command"

4. Review the generated command and its explanation

5. Click "Execute" to run the command (if desired)

## API Endpoints

- `GET /`: Web interface
- `GET /stream`: SSE endpoint for real-time command generation
  - Parameters:
    - `prompt`: The user's natural language request
    - `model`: (Optional) The Ollama model to use

## Configuration

You can configure the application by setting environment variables:

- `OLLAMA_API_URL`: URL of the Ollama API (default: `http://localhost:11434`)
- `DEFAULT_MODEL`: Default model to use (default: `llama3`)

## Security Considerations

- Commands are not executed automatically - user confirmation is required
- The application runs locally by default
- Review all generated commands before execution
- Use in a controlled environment when testing unknown commands

## Development

To contribute or modify the application:

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Run the development server with hot reload:
   ```bash
   uvicorn fastapi_app:app --reload
   ```

## Troubleshooting

- Ensure Ollama is running and accessible at the configured URL
- Check the browser console for JavaScript errors
- Review the server logs for any Python exceptions
- Verify that the selected model is downloaded and available in Ollama

## License

[MIT License](LICENSE)
