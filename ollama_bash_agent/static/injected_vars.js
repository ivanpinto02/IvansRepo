// This file sets window variables from server-injected JSON

// Function to safely initialize variables
function initializeInjectedVariables() {
    // Ensure _injected exists
    if (typeof window._injected === 'undefined') {
        console.warn('_injected object not found, initializing with defaults');
        window._injected = {};
    }
    
    // Set default values for all expected properties
    const defaults = {
        prompt: '',
        model: 'llama3',
        bash_command: '',
        output: '',
        error: null,
        raw_model_output: '',
        history: []
    };
    
    // Apply defaults and merge with injected values
    for (const [key, defaultValue] of Object.entries(defaults)) {
        if (window._injected[key] === undefined) {
            window[`_${key}`] = defaultValue;
        } else {
            window[`_${key}`] = window._injected[key];
        }
    }
    
    console.log('Injected variables initialized:', {
        prompt: window._prompt,
        model: window._model,
        bash_command: window._bash_command,
        output: window._output,
        error: window._error,
        raw_model_output: window._raw_model_output,
        history: window._history
    });
}

// Initialize when the DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeInjectedVariables);
} else {
    initializeInjectedVariables();
}
