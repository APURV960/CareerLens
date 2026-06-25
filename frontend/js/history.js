/**
 * CareerLens Search History Page Controller
 */

document.addEventListener('DOMContentLoaded', async () => {
    const historyLoader = document.getElementById('historyLoader');
    const emptyHistoryState = document.getElementById('emptyHistoryState');
    const historyGrid = document.getElementById('historyGrid');
    const clearSessionBtn = document.getElementById('clearSessionBtn');
    
    const alertContainer = document.getElementById('alertContainer');
    const sessionText = document.getElementById('sessionText');

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

    // Fetch and render historical runs
    try {
        const runs = await CareerLensAPI.getHistory();
        historyLoader.style.display = 'none';

        if (!runs || runs.length === 0) {
            emptyHistoryState.style.display = 'block';
            historyGrid.style.display = 'none';
            return;
        }

        emptyHistoryState.style.display = 'none';
        historyGrid.style.display = 'grid';
        historyGrid.innerHTML = '';

        runs.forEach(run => {
            const card = document.createElement('div');
            card.className = 'history-card glass-card';
            
            const startedDate = run.started_at ? new Date(run.started_at).toLocaleString() : 'Date Unknown';
            
            // Map status styling
            let badgeClass = 'badge-secondary'; // default
            if (run.status === 'running') badgeClass = 'badge-warning';
            if (run.status === 'failed') badgeClass = 'badge-danger'; // wait, style supports red or fallback
            
            // We set status text and color
            const statusHtml = `<span class="badge ${badgeClass}" style="text-transform: uppercase;">${run.status}</span>`;
            
            card.innerHTML = `
                <div>
                    <div class="history-date">${startedDate}</div>
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.1rem; color: var(--text-primary);">Search Run</h3>
                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
                        Resume ID: #${run.resume_id}
                    </div>
                </div>
                <div>
                    <div class="history-status-badge">
                        Status: ${statusHtml}
                    </div>
                    <a href="results.html?run_id=${run.run_id}" class="btn btn-secondary btn-sm" style="width: 100%; justify-content: center; margin-top: 0.5rem; text-decoration: none;">
                        <span>View Results</span> <span>→</span>
                    </a>
                </div>
            `;
            historyGrid.appendChild(card);
        });

    } catch (error) {
        historyLoader.style.display = 'none';
        showToast(`Failed to load history: ${error.message}`, 'error');
        emptyHistoryState.style.display = 'block';
        emptyHistoryState.querySelector('h2').textContent = 'Error Loading History';
        emptyHistoryState.querySelector('p').textContent = error.message;
    }

    // Reset session logic
    clearSessionBtn.addEventListener('click', () => {
        const confirmClear = confirm('Are you sure you want to reset your session?\n\nThis will clear your local resume version history, delete your anonymous session key, and generate a new session. Your database entries will remain, but you will start fresh in a brand new session.');
        
        if (confirmClear) {
            CareerLensAPI.resetSession();
        }
    });
});
