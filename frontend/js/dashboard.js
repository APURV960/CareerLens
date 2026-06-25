/**
 * CareerLens Dashboard Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const resumeChecking = document.getElementById('resumeChecking');
    const noResumeState = document.getElementById('noResumeState');
    const hasResumeState = document.getElementById('hasResumeState');
    const activeVerText = document.getElementById('activeVerText');
    const alertContainer = document.getElementById('alertContainer');
    const sessionText = document.getElementById('sessionText');
    
    // KPI widgets
    const statResumeScore = document.getElementById('statResumeScore');
    const statJobsFound = document.getElementById('statJobsFound');
    const statHighestMatch = document.getElementById('statHighestMatch');
    const statMissingSkills = document.getElementById('statMissingSkills');
    const statSearchRuns = document.getElementById('statSearchRuns');
    const statApplicationsSent = document.getElementById('statApplicationsSent');

    // Funnel bars and counters
    const barGenerated = document.getElementById('barGenerated');
    const countGenerated = document.getElementById('countGenerated');
    const barApplied = document.getElementById('barApplied');
    const countApplied = document.getElementById('countApplied');
    const barInterview = document.getElementById('barInterview');
    const countInterview = document.getElementById('countInterview');
    const barOffer = document.getElementById('barOffer');
    const countOffer = document.getElementById('countOffer');
    const barRejected = document.getElementById('barRejected');
    const countRejected = document.getElementById('countRejected');

    // Activity List
    const activityList = document.getElementById('activityList');

    // Trigger buttons
    const runAgentBtn = document.getElementById('runAgentBtn');
    const dashboardRunBtn = document.getElementById('dashboardRunBtn');
    
    // Overlay elements
    const processingOverlay = document.getElementById('processingOverlay');
    const processingTitle = document.getElementById('processingTitle');
    const statusLog = document.getElementById('statusLog');
    const errorActions = document.getElementById('errorActions');
    const closeOverlayBtn = document.getElementById('closeOverlayBtn');
    const retryAgentBtn = document.getElementById('retryAgentBtn');

    let pollInterval = null;
    let consecutiveErrors = 0;
    const MAX_POLLING_ERRORS = 5;

    // Display current session ID
    if (sessionText) {
        const sid = getOrCreateSessionId();
        sessionText.textContent = sid.substring(0, 8) + '...';
        sessionText.title = `Full Session ID: ${sid}`;
    }

    // Helper to display toast notifications
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.innerHTML = `
            <span>${message}</span>
            <button class="alert-close">&times;</button>
        `;
        alertContainer.appendChild(toast);
        toast.querySelector('.alert-close').addEventListener('click', () => toast.remove());
        setTimeout(() => { if (toast.parentElement) toast.remove(); }, 5000);
    }

    // Append log message to the pseudo-console
    function appendLog(message, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `status-log-entry ${type}`;
        const time = new Date().toLocaleTimeString();
        entry.textContent = `[${time}] ${message}`;
        statusLog.appendChild(entry);
        statusLog.scrollTop = statusLog.scrollHeight;
    }

    // Helper for relative times
    function getRelativeTime(timestamp) {
        if (!timestamp) return 'Recently';
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffMins < 1) return 'Just now';
            if (diffMins < 60) return `${diffMins}m ago`;
            if (diffHours < 24) return `${diffHours}h ago`;
            return `${diffDays}d ago`;
        } catch (e) {
            return 'Recently';
        }
    }

    // Load dashboard stats
    async function loadDashboardStats() {
        try {
            const stats = await CareerLensAPI.getDashboardStats();
            resumeChecking.style.display = 'none';

            if (!stats.has_resume) {
                noResumeState.style.display = 'block';
                hasResumeState.style.display = 'none';
                localStorage.removeItem('resume_id');
                return;
            }

            localStorage.setItem('resume_id', 'active_resume'); // Lock active resume state locally
            noResumeState.style.display = 'none';
            hasResumeState.style.display = 'block';

            // Bind values
            statResumeScore.textContent = `${stats.resume_score}/100`;
            statJobsFound.textContent = stats.jobs_found;
            statHighestMatch.textContent = stats.highest_match > 0 ? `${stats.highest_match}%` : 'N/A';
            statMissingSkills.textContent = stats.missing_skills_count;
            statSearchRuns.textContent = stats.search_runs_count;
            statApplicationsSent.textContent = stats.applications_sent;

            // Update tracker funnel percentages
            const breakdown = stats.app_breakdown || {};
            const totalApps = Object.values(breakdown).reduce((a, b) => a + b, 0) || 1;
            
            const setFunnelRow = (barEl, countEl, statusVal) => {
                const count = breakdown[statusVal] || 0;
                countEl.textContent = count;
                const pct = ((count / totalApps) * 100).toFixed(0);
                barEl.style.width = count > 0 ? `${Math.max(12, pct)}%` : '0%';
            };

            setFunnelRow(barGenerated, countGenerated, 'Generated');
            setFunnelRow(barApplied, countApplied, 'Applied');
            setFunnelRow(barInterview, countInterview, 'Interview');
            setFunnelRow(barOffer, countOffer, 'Offer');
            setFunnelRow(barRejected, countRejected, 'Rejected');

            // Render activities
            activityList.innerHTML = '';
            if (stats.recent_activity && stats.recent_activity.length > 0) {
                stats.recent_activity.forEach(act => {
                    let icon = '⚡';
                    if (act.type === 'upload') icon = '📄';
                    if (act.type === 'run') icon = '🤖';
                    if (act.type === 'application') icon = '✉';

                    const item = document.createElement('div');
                    item.className = 'activity-item';
                    item.innerHTML = `
                        <span class="activity-icon">${icon}</span>
                        <div class="activity-details">
                            <div class="activity-message">${act.message}</div>
                            <div class="activity-time">${getRelativeTime(act.timestamp)}</div>
                        </div>
                    `;
                    activityList.appendChild(item);
                });
            } else {
                activityList.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem 0;">No activities logged.</div>';
            }

        } catch (err) {
            console.error(err);
            resumeChecking.style.display = 'none';
            // If API check fails, fall back to check localStorage
            const resumeId = localStorage.getItem('resume_id');
            if (resumeId) {
                noResumeState.style.display = 'none';
                hasResumeState.style.display = 'block';
                showToast('Offline mode: Could not fetch latest stats from database.', 'warning');
            } else {
                noResumeState.style.display = 'block';
            }
        }
    }

    // Extend window-level API call to results
    CareerLensAPI.getDashboardStats = async function() {
        return await apiRequest('/results/dashboard-stats', { method: 'GET' });
    };

    loadDashboardStats();

    // Trigger Agent execution
    async function triggerAgent() {
        processingOverlay.classList.add('active');
        errorActions.style.display = 'none';
        statusLog.innerHTML = '';
        processingTitle.textContent = 'Queueing Agent Task...';
        consecutiveErrors = 0;

        appendLog('Initializing CareerLens AI Agent...', 'info');
        appendLog('Requesting background task authorization...', 'info');

        try {
            const result = await CareerLensAPI.runAgent();
            appendLog(`Agent run registered. Job ID: ${result.job_id}`, 'success');
            appendLog(`Initial state: ${result.status}`, 'info');
            
            // Start polling
            startPolling(result.job_id);
        } catch (error) {
            appendLog(`Trigger failure: ${error.message}`, 'error');
            showToast('Failed to trigger agent.', 'error');
            showErrorState();
        }
    }

    // Polling Status Logic
    function startPolling(jobId) {
        if (pollInterval) clearInterval(pollInterval);
        
        let lastStatus = '';
        appendLog('Starting live status polling (2.5s interval)...', 'info');

        pollInterval = setInterval(async () => {
            try {
                const statusData = await CareerLensAPI.getRunStatus(jobId);
                consecutiveErrors = 0; // Reset errors on successful API call

                if (statusData.status !== lastStatus) {
                    lastStatus = statusData.status;
                    appendLog(`Job state changed: ${statusData.status.toUpperCase()}`, 'info');
                    
                    if (statusData.status === 'running') {
                        processingTitle.textContent = 'Agent Analyzing...';
                        appendLog('Agent is executing pipeline: scraping websites, calculating semantic ranking embeddings, detecting skill gaps, and generating cover letters.', 'info');
                    }
                }

                if (statusData.status === 'completed') {
                    appendLog('Pipeline finished execution!', 'success');
                    clearInterval(pollInterval);
                    
                    if (statusData.run_id) {
                        appendLog(`Redirecting to Results Page (Run ID: ${statusData.run_id.substring(0, 8)}...)`, 'success');
                        setTimeout(() => {
                            window.location.href = `results.html?run_id=${statusData.run_id}`;
                        }, 1500);
                    } else {
                        appendLog('Job completed but run_id was not returned. Fetching latest run from history...', 'warning');
                        try {
                            const history = await CareerLensAPI.getHistory();
                            if (history && history.length > 0) {
                                const latestRun = history[0]; 
                                window.location.href = `results.html?run_id=${latestRun.run_id}`;
                            } else {
                                throw new Error('No search run record found in history.');
                            }
                        } catch (histErr) {
                            appendLog(`Redirection failed: ${histErr.message}`, 'error');
                            showErrorState();
                        }
                    }
                } else if (statusData.status === 'failed') {
                    appendLog(`Job execution failed: ${statusData.error_message || 'Internal Agent Failure'}`, 'error');
                    clearInterval(pollInterval);
                    showErrorState();
                }

            } catch (error) {
                consecutiveErrors++;
                appendLog(`Polling glitch (${consecutiveErrors}/${MAX_POLLING_ERRORS}): ${error.message}`, 'warning');
                
                if (consecutiveErrors >= MAX_POLLING_ERRORS) {
                    appendLog('Polling aborted. Too many consecutive network failures.', 'error');
                    clearInterval(pollInterval);
                    showErrorState();
                }
            }
        }, 2500);
    }

    function showErrorState() {
        processingTitle.textContent = 'Agent Pipeline Stopped';
        errorActions.style.display = 'flex';
    }

    // Event Bindings
    if (runAgentBtn) runAgentBtn.addEventListener('click', triggerAgent);
    if (dashboardRunBtn) dashboardRunBtn.addEventListener('click', triggerAgent);
    if (retryAgentBtn) retryAgentBtn.addEventListener('click', triggerAgent);
    
    if (closeOverlayBtn) {
        closeOverlayBtn.addEventListener('click', () => {
            processingOverlay.classList.remove('active');
            if (pollInterval) clearInterval(pollInterval);
            loadDashboardStats(); // Refresh dashboard data when closing the overlay
        });
    }
});
