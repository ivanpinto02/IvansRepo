import sys
print('PYTHON sys.path:')
for p in sys.path:
    print('  ', p)
try:
    import flask
    print('flask module location:', flask.__file__)
except Exception as e:
    print('Could not import flask:', e)
try:
    import jinja2
    print('jinja2 module location:', jinja2.__file__)
except Exception as e:
    print('Could not import jinja2:', e)
from flask import Flask, render_template

app = Flask(__name__)

from jinja2.runtime import Undefined

def _safe(val, fallback=None):
    # Replace Jinja2 Undefined or unserializable values with a safe fallback
    if isinstance(val, Undefined):
        return fallback
    if isinstance(val, (str, bool, int, float)) or val is None:
        return val
    if isinstance(val, (list, tuple)):
        return [ _safe(v, fallback) for v in val ]
    if isinstance(val, dict):
        return { k: _safe(v, fallback) for k, v in val.items() }
    return fallback

def safe_template_context(**kwargs):
    # Provide safe defaults for all variables expected by index.html
    defaults = {
        'prompt': '',
        'model': 'llama3',
        'models': ['llama3', 'deepseek-coder:1.3b'],
        'bash_command': None,
        'approved': False,
        'error': None,
        'output': None,
        'steps': None,
        'raw_model_output': None,
        'history': [],
    }
    defaults.update(kwargs)
    # Force all values to safe types
    safe_context = {k: _safe(v, defaults.get(k)) for k, v in defaults.items()}
    # Log the type of each variable
    print('--- Template Context Types ---')
    for k, v in safe_context.items():
        print(f"{k}: {type(v)} -> {repr(v)}")
    print('-----------------------------')
    return safe_context

import traceback

@app.route('/')
def index():
    context = safe_template_context()
    print('Rendering template: index.html')
    print('Template context:', context)
    for k, v in context.items():
        print(f"[DEBUG] {k}: {type(v)} -> {repr(v)}")
    return render_template('index.html', **context)

@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error and template context
    print('Exception occurred:', e)
    print('Traceback:')
    traceback.print_exc()
    return f"<h1>500 Internal Server Error</h1><pre>{str(e)}</pre>", 500

if __name__ == '__main__':
    app.run(debug=True, port=8000, use_reloader=False)
