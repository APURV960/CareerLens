/**
 * CareerLens Central API Client
 * Manages connections, headers, session tracking, and error mapping
 */

const API_CONFIG = {
    BASE_URL: window.location.port === '8000' || (!window.location.origin.includes('localhost') && !window.location.origin.includes('127.0.0.1'))
        ? `${window.location.origin}/api`
        : 'http://localhost:8000/api',
    getOrigin() {
        return this.BASE_URL;
    }
};

/**
 * Retrieves the current session UUID or generates a new one.
 * Maps to Mode A anonymous session validation on the backend.
 */
function getOrCreateSessionId() {
    let sessionId = localStorage.getItem('x_session_id');
    if (!sessionId) {
        // Generate a cryptographically secure UUID or fallback to random math
        if (typeof crypto !== 'undefined' && crypto.randomUUID) {
            sessionId = crypto.randomUUID();
        } else {
            sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                const r = Math.random() * 16 | 0;
                const v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        }
        localStorage.setItem('x_session_id', sessionId);
    }
    return sessionId;
}

/**
 * Centralized fetch helper with custom headers and error handling
 */
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    
    // Ensure headers exist
    options.headers = options.headers || {};
    
    // Add anonymous session identifier
    options.headers['X-Session-ID'] = getOrCreateSessionId();
    
    try {
        const response = await fetch(url, options);
        
        // Handle server/network errors
        if (!response.ok) {
            let errorMessage = 'An error occurred while communicating with the server.';
            const clone = response.clone();
            try {
                const errData = await response.json();
                errorMessage = errData.detail || errorMessage;
            } catch (e) {
                // If response is not JSON, get raw text or default
                try {
                    errorMessage = await clone.text() || errorMessage;
                } catch (textErr) {
                    // Ignore text reading error
                }
            }
            const error = new Error(errorMessage);
            error.status = response.status;
            throw error;
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error on ${endpoint}:`, error);
        
        // Differentiate network failures from server exceptions
        if (!error.status) {
            error.message = 'Network connectivity issue. Please check if the backend server is running on port 8000.';
        }
        throw error;
    }
}

/**
 * Exports API client methods
 */
const CareerLensAPI = {
    /**
     * Upload resume PDF
     * @param {File} file 
     */
    async uploadResume(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Note: fetch will auto-set the Content-Type header with the boundary for FormData
        return await apiRequest('/uploads/resume', {
            method: 'POST',
            body: formData
        });
    },

    /**
     * Start the AI career agent pipeline
     */
    async runAgent() {
        return await apiRequest('/agent/run', {
            method: 'POST'
        });
    },

    /**
     * Poll current status of background agent execution
     * @param {string} jobId 
     */
    async getRunStatus(jobId) {
        return await apiRequest(`/agent/status/${jobId}`, {
            method: 'GET'
        });
    },

    /**
     * Retrieve job match results and skill gaps
     * @param {string} runId 
     */
    async getRunResults(runId) {
        return await apiRequest(`/results/run/${runId}`, {
            method: 'GET'
        });
    },

    /**
     * Retrieve list of past agent run jobs executed by this session
     */
    async getHistory() {
        return await apiRequest('/results/history', {
            method: 'GET'
        });
    },

    /**
     * Download Excel report of results
     * Fetches file as a Blob with X-Session-ID, then triggers local save
     */
    async exportResults(runId) {
        const url = `${API_CONFIG.BASE_URL}/results/run/${runId}/export`;
        const headers = {
            'X-Session-ID': getOrCreateSessionId()
        };
        
        try {
            const response = await fetch(url, { headers });
            if (!response.ok) {
                throw new Error('Failed to generate export file.');
            }
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `job_matches_run_${runId.substring(0, 8)}.xlsx`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        } catch (error) {
            console.error('Export Error:', error);
            throw new Error('Could not export matches. Please make sure the run completed successfully.');
        }
    },

    /**
     * Resets session to start fresh
     */
    resetSession() {
        localStorage.removeItem('x_session_id');
        localStorage.removeItem('resume_id');
        window.location.reload();
    }
};
