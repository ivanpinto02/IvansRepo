// main.js - All main interactive and logging JS logic for Ollama Bash Agent

// Initialize SSE client
let sseClient = null;

// DOM Elements
const promptForm = document.getElementById('prompt-form');
const outputDiv = document.getElementById('stream-output');
const spinner = document.getElementById('loading-spinner');

// Log initial state
function logInitialState() {
    if (window._prompt) console.log('Prompt:', window._prompt);
    if (window._model) console.log('Model:', window._model);
    if (window._bash_command) console.log('Generated Command:', window._bash_command);
    if (window._output) console.log('Command Output:', window._output);
    if (window._raw_model_output) console.log('Raw Model Output:', window._raw_model_output);
    if (window._history) console.log('History:', window._history);
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const prompt = form.prompt?.value.trim();
    const model = form.model?.value || 'llama3';
    const isApprove = form.approve?.value === '1';
    
    if (!prompt) return;
    
    // Log the action
    const actionType = isApprove ? 'Approve & Run' : 'Generate & Run';
    console.log(`[${actionType}] Prompt: ${prompt} | Model: ${model}`);
    
    // Clear previous output
    if (outputDiv) outputDiv.textContent = '';
    
    // Show loading spinner
    if (spinner) spinner.style.display = 'block';
    
    // Close any existing connection
    if (sseClient) {
        sseClient.close();
        sseClient = null;
    }
    
    // Create a new SSE client
    sseClient = new SSEClient();
    
    // Build the SSE URL
    const url = `/stream?prompt=${encodeURIComponent(prompt)}&model=${encodeURIComponent(model)}&_=${Date.now()}`;
    
    // Connect to the SSE endpoint
    sseClient.connect(
        url,
        // onMessage handler
        (event) => {
            try {
                if (!event.data) return;
                
                // Parse the event data
                const lines = event.data.split('\n');
                let eventType = 'message';
                let data = '';
                
                // Parse the SSE message format
                for (const line of lines) {
                    if (line.startsWith('event:')) {
                        eventType = line.substring(6).trim();
                    } else if (line.startsWith('data:')) {
                        data = line.substring(5).trim();
                    }
                }
                
                // Handle different event types
                switch (eventType) {
                    case 'status':
                        console.log('Status:', data);
                        break;
                        
                    case 'error':
                        console.error('Server error:', data);
                        if (outputDiv) {
                            outputDiv.textContent += `\n[Error] ${data}\n`;
                            outputDiv.scrollTop = outputDiv.scrollHeight;
                        }
                        break;
                        
                    case 'end':
                        console.log('Stream ended');
                        if (spinner) spinner.style.display = 'none';
                        break;
                        
                    case 'message':
                    default:
                        if (outputDiv) {
                            outputDiv.textContent += data;
                            outputDiv.scrollTop = outputDiv.scrollHeight;
                        }
                }
            } catch (error) {
                console.error('Error processing message:', error);
            }
        },
        // onError handler
        (error) => {
            console.error('SSE error:', error);
            if (spinner) spinner.style.display = 'none';
            
            if (outputDiv) {
                outputDiv.textContent += '\n[Error] Connection error. Please try again.\n';
                outputDiv.scrollTop = outputDiv.scrollHeight;
            }
        },
        // onOpen handler
        () => {
            console.log('SSE connection opened');
            if (outputDiv) {
                outputDiv.textContent = '';
            }
        }
    );
}

// Set up event listeners
function setupEventListeners() {
    // Form submission
    if (promptForm) {
        promptForm.addEventListener('submit', handleFormSubmit);
    }
    
    // Log download button clicks
    document.querySelectorAll('form[action="/download"]').forEach(form => {
        form.addEventListener('submit', () => {
            console.log('[Download Output]');
        });
    });
    
    // Log replay button clicks
    document.querySelectorAll('form button').forEach(btn => {
        if (btn.textContent.trim() === 'Replay') {
            btn.addEventListener('click', function() {
                const prompt = btn.parentElement.querySelector('input[name="prompt"]')?.value;
                const model = btn.parentElement.querySelector('input[name="model"]')?.value || 'llama3';
                console.log('[Replay] Prompt:', prompt, '| Model:', model);
            });
        }
    });
}

// Initialize when the DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        logInitialState();
        setupEventListeners();
    });
} else {
    logInitialState();
    setupEventListeners();
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (sseClient) {
        sseClient.close();
    }
});
