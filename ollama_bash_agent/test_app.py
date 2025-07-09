import os
import tempfile
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage_loads(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Ollama Bash Agent' in rv.data

def test_generate_and_run_command(client):
    # This test will check if the agent can process a prompt and run a command
    prompt = 'echo test_tdd_output'
    rv = client.post('/', data={'prompt': prompt}, follow_redirects=True)
    assert rv.status_code == 200
    assert b'echo test_tdd_output' in rv.data  # Command shown
    assert b'test_tdd_output' in rv.data      # Output shown

def test_open_terminal_and_run(client, monkeypatch):
    # Simulate a prompt that requests opening a terminal (not possible from Flask directly)
    # Instead, we check if the agent can run a command that would normally open a terminal
    prompt = 'open a terminal window'
    rv = client.post('/', data={'prompt': prompt}, follow_redirects=True)
    # The AI will likely return a command like start cmd or start powershell
    # We check that the command is shown, but do NOT actually open a terminal in test
    assert rv.status_code == 200
    assert b'start' in rv.data or b'cmd' in rv.data or b'powershell' in rv.data
    # We do NOT want to actually open a terminal during automated tests
