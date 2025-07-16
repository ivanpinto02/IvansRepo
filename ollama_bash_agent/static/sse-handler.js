class SSEClient {
    constructor() {
        this.eventSource = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 1000; // Start with 1 second
        this.lastEventId = '';
        this.isProcessing = false;
    }

    connect(url, onMessage, onError, onOpen) {
        // Close any existing connection
        this.close();

        // Reset state
        this.reconnectAttempts = 0;
        this.eventSource = new EventSource(url);
        this.isProcessing = true;

        // Set up event handlers
        this.eventSource.onopen = (event) => {
            console.log('SSE connection established');
            this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
            if (onOpen) onOpen(event);
        };

        this.eventSource.onmessage = (event) => {
            try {
                if (event.lastEventId) {
                    this.lastEventId = event.lastEventId;
                }
                if (onMessage) onMessage(event);
            } catch (error) {
                console.error('Error processing message:', error);
            }
        };

        this.eventSource.onerror = (error) => {
            console.error('SSE connection error:', error);
            
            // Only try to reconnect if the connection was actually established before
            if (this.eventSource.readyState === EventSource.CLOSED) {
                this.attemptReconnect(url, onMessage, onError, onOpen);
            } else if (onError) {
                onError(error);
            }
        };

        return this;
    }

    attemptReconnect(url, onMessage, onError, onOpen) {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            if (onError) onError(new Error('Max reconnection attempts reached'));
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms...`);
        
        setTimeout(() => {
            if (this.isProcessing) { // Only reconnect if still needed
                this.connect(url, onMessage, onError, onOpen);
            }
        }, Math.min(delay, 30000)); // Max 30 seconds delay
    }

    close() {
        if (this.eventSource) {
            try {
                // Remove all event listeners
                this.eventSource.onopen = null;
                this.eventSource.onmessage = null;
                this.eventSource.onerror = null;
                
                // Close the connection
                if (this.eventSource.readyState !== EventSource.CLOSED) {
                    this.eventSource.close();
                }
                console.log('SSE connection closed');
            } catch (error) {
                console.error('Error closing SSE connection:', error);
            } finally {
                this.eventSource = null;
                this.isProcessing = false;
            }
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SSEClient;
}
