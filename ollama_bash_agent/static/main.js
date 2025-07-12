// main.js - All main interactive and logging JS logic for Ollama Bash Agent

document.addEventListener('DOMContentLoaded', function() {
  // Log initial state only if defined
  if (window._prompt) console.log('Prompt:', JSON.stringify(window._prompt));
  if (window._model) console.log('Model:', JSON.stringify(window._model));
  if (window._bash_command) console.log('Generated Command:', JSON.stringify(window._bash_command));
  if (window._output) console.log('Command Output:', JSON.stringify(window._output));
  if (window._raw_model_output) console.log('Raw Model Output:', JSON.stringify(window._raw_model_output));
  if (window._history) console.log('History:', JSON.stringify(window._history));

  // Log form submissions
  document.getElementById('prompt-form')?.addEventListener('submit', function(e) {
    const form = e.target;
    const prompt = form.prompt?.value;
    const model = form.model?.value;
    const approve = form.approve?.value;
    if (approve) {
      console.log('[Approve & Run] Prompt:', prompt, '| Model:', model);
    } else {
      console.log('[Generate & Run] Prompt:', prompt, '| Model:', model);
    }
  });

  // Log download button
  document.querySelectorAll('form[action="/download"]').forEach(f => {
    f.addEventListener('submit', function(e) {
      console.log('[Download Output]');
    });
  });

  // Log replay buttons
  document.querySelectorAll('form button').forEach(btn => {
    if (btn.textContent.trim() === 'Replay') {
      btn.addEventListener('click', function() {
        const prompt = btn.parentElement.querySelector('input[name="prompt"]').value;
        const model = btn.parentElement.querySelector('input[name="model"]').value;
        console.log('[Replay] Prompt:', prompt, '| Model:', model);
      });
    }
  });
});
