# Ollama Bash Agent Web App

This project is a cleaned-up, production-ready Flask web agent for running and managing Bash commands via a modern web UI.

## Features
- **Flask-based web server** with a single entry point (`main.py`)
- **Modern UI** using HTML/CSS/JS in the `templates/` and `static/` folders
- **Defensive template context**: All variables passed to templates are guaranteed to be safe and JSON-serializable, eliminating Jinja2 `Undefined` errors
- **Minimal dependencies**: See `requirements.txt` for essentials only
- **Clean project structure**: All unused/test files have been removed for clarity and maintainability

## Project Structure
```
ollama_bash_agent/
  main.py            # Main Flask application
  requirements.txt   # Python dependencies
  templates/         # HTML templates (index.html, etc.)
  static/            # JS/CSS for the UI
  .venv/             # (optional) Python virtual environment
```

## How to Run
1. **Create and activate a virtual environment:**
   ```sh
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate.bat
   # On Unix/Mac:
   source .venv/bin/activate
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Start the web agent:**
   ```sh
   python main.py
   ```
4. **Visit** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Troubleshooting
- If you see a 500 error, check the terminal for debug output.
- The app now ensures all template variables are always provided and serializable.
- For further issues, ensure your virtual environment is activated and dependencies are installed.

---

Project maintained by Ivan Pinto. Cleaned and refactored with help from AI coding assistant.
