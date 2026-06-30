/**
 * CareerLens Results Page Controller
 */

async function initResults() {
    const urlParams = new URLSearchParams(window.location.search);
    const runId = urlParams.get('run_id');

    const resultsSubheading = document.getElementById('resultsSubheading');
    const exportBtn = document.getElementById('exportBtn');
    
    // Section elements
    const jobsTableBody = document.getElementById('jobsTableBody');
    const marketDemandList = document.getElementById('marketDemandList');
    const skillsGuidanceGrid = document.getElementById('skillsGuidanceGrid');
    const lettersContainer = document.getElementById('lettersContainer');
    
    // Metadata elements
    const runIdVal = document.getElementById('runIdVal');
    const runStatusVal = document.getElementById('runStatusVal');
    const runStartedVal = document.getElementById('runStartedVal');
    const runCompletedVal = document.getElementById('runCompletedVal');
    
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

    if (!runId) {
        showToast('No search run ID specified. Redirecting to history...', 'error');
        setTimeout(() => { window.location.href = 'history.html'; }, 3000);
        return;
    }

    runIdVal.textContent = runId;

    // Load all results data
    try {
        const [results, history] = await Promise.all([
            CareerLensAPI.getRunResults(runId),
            CareerLensAPI.getHistory()
        ]);

        resultsSubheading.textContent = `Job discovery and skill analysis for Run ID: ${runId.substring(0, 8)}...`;
        exportBtn.removeAttribute('disabled');

        // Bind export button click
        exportBtn.addEventListener('click', async () => {
            exportBtn.setAttribute('disabled', 'true');
            const originalText = exportBtn.innerHTML;
            exportBtn.innerHTML = '<span>⏳ Downloading...</span>';
            try {
                await CareerLensAPI.exportResults(runId);
                showToast('Results exported to Excel successfully!', 'success');
            } catch (err) {
                showToast(err.message, 'error');
            } finally {
                exportBtn.innerHTML = originalText;
                exportBtn.removeAttribute('disabled');
            }
        });

        // 1. Render matched jobs
        renderMatchedJobs(results.jobs);

        // 2. Render skill gaps & guidance dashboard
        renderSkillGap(results.skill_gap, results.jobs.length);

        // 3. Render cover letters (with inline editor triggers)
        renderCoverLetters(results.cover_letters);

        // 4. Render metadata details from history
        renderMetadata(history, runId);

    } catch (error) {
        showToast(error.message, 'error');
        jobsTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center" style="color: var(--color-danger); padding: 3rem; font-weight: 500;">
                    ⚠️ Failed to load results. ${error.message}
                </td>
            </tr>
        `;
    }

    /**
     * Renders Section 1: Jobs Table
     */
    function renderMatchedJobs(jobs) {
        jobsTableBody.innerHTML = '';
        if (!jobs || jobs.length === 0) {
            jobsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center" style="color: var(--text-muted); padding: 3rem;">
                        No jobs matched your resume. Try adding more skills or updating your resume text.
                    </td>
                </tr>
            `;
            return;
        }

        jobs.forEach(job => {
            const scorePercentage = (job.match_score * 100).toFixed(0);
            
            // Determine match quality text and classes
            let matchText = 'Weak Match';
            let matchClass = 'match-weak';
            let scoreBarClass = 'weak';
            
            if (job.match_score >= 0.85) {
                matchText = 'Excellent Match';
                matchClass = 'match-excellent';
                scoreBarClass = 'excellent';
            } else if (job.match_score >= 0.70) {
                matchText = 'Good Match';
                matchClass = 'match-good';
                scoreBarClass = 'good';
            } else if (job.match_score >= 0.50) {
                matchText = 'Moderate Match';
                matchClass = 'match-moderate';
                scoreBarClass = 'moderate';
            }

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div style="font-weight: 600; color: var(--text-primary); font-family: var(--font-heading);">${job.title}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); font-family: var(--font-sans); margin-top: 0.25rem;">
                        Source: ${job.source} | Salary: ${job.salary} | Posted: ${job.posted_at}
                    </div>
                </td>
                <td style="color: var(--text-secondary); font-weight: 500;">${job.company}</td>
                <td>
                    <div style="color: var(--text-secondary);">${job.location}</div>
                    <span class="badge badge-teal" style="font-size: 0.7rem; margin-top: 0.25rem; padding: 0.1rem 0.4rem;">${job.work_setting}</span>
                </td>
                <td>
                    <span class="badge" style="font-size: 0.75rem;">${job.experience_level}</span>
                </td>
                <td>
                    <div class="score-bar-container" style="flex-direction: column; align-items: flex-start; gap: 0.25rem;">
                        <span class="match-badge ${matchClass}">${matchText} (${scorePercentage}%)</span>
                        <div class="score-bar-outer" style="width: 100%;">
                            <div class="score-bar-inner ${scoreBarClass}" style="width: ${scorePercentage}%"></div>
                        </div>
                    </div>
                </td>
                <td>
                    <select class="tracker-select" data-job-id="${job.id}">
                        <option value="Generated" ${job.application_status === 'Generated' ? 'selected' : ''}>Generated</option>
                        <option value="Applied" ${job.application_status === 'Applied' ? 'selected' : ''}>Applied</option>
                        <option value="Interview" ${job.application_status === 'Interview' ? 'selected' : ''}>Interview</option>
                        <option value="Offer" ${job.application_status === 'Offer' ? 'selected' : ''}>Offer</option>
                        <option value="Rejected" ${job.application_status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                    </select>
                </td>
                <td>
                    <a href="${job.original_apply_url || job.url}" target="_blank" class="btn btn-secondary btn-sm" style="padding: 0.35rem 0.75rem; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 0.25rem;">
                        <span>Apply</span> <span>↗</span>
                    </a>
                </td>
            `;

            // Bind Tracker Dropdown Event Listener
            const selectEl = tr.querySelector('.tracker-select');
            selectEl.addEventListener('change', async (e) => {
                const jobIdVal = e.target.getAttribute('data-job-id');
                const statusVal = e.target.value;
                selectEl.setAttribute('disabled', 'true');
                try {
                    await apiRequest('/results/applications/status', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            job_result_id: parseInt(jobIdVal),
                            status: statusVal
                        })
                    });
                    showToast(`Application status updated to '${statusVal}' for ${job.company}!`, 'success');
                } catch (err) {
                    showToast(err.message, 'error');
                    // Reset value on error
                    e.target.value = job.application_status;
                } finally {
                    selectEl.removeAttribute('disabled');
                }
            });

            jobsTableBody.appendChild(tr);
        });
    }

    /**
     * Renders Section 2: Gaps & Skill Guidance Cards
     */
    function renderSkillGap(skillGap, jobCount) {
        // Render Market Demand Progress list
        marketDemandList.innerHTML = '';
        if (skillGap && skillGap.market_demand && skillGap.market_demand.length > 0) {
            const totalJobs = jobCount || 1;
            
            skillGap.market_demand.forEach(([skill, count]) => {
                const percentage = ((count / totalJobs) * 100).toFixed(0);
                
                const item = document.createElement('div');
                item.className = 'demand-item';
                item.innerHTML = `
                    <div class="demand-skill" style="text-transform: capitalize;">${skill}</div>
                    <div class="demand-value" style="width: 70%;">
                        <div class="demand-progress-outer">
                            <div class="demand-progress-inner" style="width: ${percentage}%;"></div>
                        </div>
                        <span class="demand-count">${percentage}%</span>
                    </div>
                `;
                marketDemandList.appendChild(item);
            });
        } else {
            marketDemandList.innerHTML = '<div style="color: var(--text-muted);">No market demand metrics available.</div>';
        }

        // Render Career Guidance Missing Skills Cards Grid
        skillsGuidanceGrid.innerHTML = '';
        if (skillGap && skillGap.missing_skills && skillGap.missing_skills.length > 0) {
            skillGap.missing_skills.forEach(skill => {
                const importanceClass = skill.importance.toLowerCase() === 'critical' ? 'critical' : 'high';
                const diffClass = skill.difficulty.toLowerCase() === 'easy' ? 'easy' : (skill.difficulty.toLowerCase() === 'hard' ? 'hard' : 'medium');
                
                const card = document.createElement('div');
                card.className = 'skill-guidance-card';
                card.innerHTML = `
                    <div class="skill-guidance-header">
                        <span class="skill-guidance-title" style="text-transform: capitalize;">${skill.name}</span>
                        <span class="badge badge-warning" style="font-size: 0.7rem; font-weight: 600;">GAP</span>
                    </div>
                    
                    <div class="skill-metadata-row">
                        <div class="skill-meta-item">
                            <span class="skill-meta-label">Importance</span>
                            <span class="skill-meta-val ${importanceClass}">${skill.importance}</span>
                        </div>
                        <div class="skill-meta-item">
                            <span class="skill-meta-label">Difficulty</span>
                            <span class="skill-meta-val ${diffClass}">${skill.difficulty}</span>
                        </div>
                        <div class="skill-meta-item">
                            <span class="skill-meta-label">Est. Time</span>
                            <span class="skill-meta-val">${skill.learning_time}</span>
                        </div>
                        <div class="skill-meta-item">
                            <span class="skill-meta-label">Demand</span>
                            <span class="skill-meta-val" style="color: var(--color-emerald)">High</span>
                        </div>
                    </div>

                    <div class="learning-resources-section">
                        <div class="resources-title">Learning Resources</div>
                        <div class="resources-grid">
                            <a href="${skill.resources.official_docs}" target="_blank" class="resource-link">
                                <span>📖 Docs</span>
                            </a>
                            <a href="${skill.resources.free_course}" target="_blank" class="resource-link">
                                <span>🎓 Course</span>
                            </a>
                            <a href="${skill.resources.youtube}" target="_blank" class="resource-link">
                                <span>▶ YouTube</span>
                            </a>
                            <a href="${skill.resources.github_project}" target="_blank" class="resource-link">
                                <span>🐙 GitHub</span>
                            </a>
                        </div>
                    </div>
                `;
                skillsGuidanceGrid.appendChild(card);
            });
        } else {
            skillsGuidanceGrid.innerHTML = `
                <div style="grid-column: 1 / -1; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.15); border-radius: var(--radius-md); padding: 3rem; text-align: center; color: var(--color-emerald); font-weight: 500;">
                    <span>🎉</span> Perfect match! Your resume contains all the technical skills required by these positions.
                </div>
            `;
        }
    }

    /**
     * Renders Section 3: Cover Letters (Inline Editor Format)
     */
    function renderCoverLetters(letters) {
        lettersContainer.innerHTML = '';
        if (!letters || letters.length === 0) {
            lettersContainer.innerHTML = `
                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 3rem; text-align: center; color: var(--text-muted);">
                    No cover letters generated for this run. (Letters are generated for top-ranked jobs).
                </div>
            `;
            return;
        }

        letters.forEach((letter, index) => {
            const editorDiv = document.createElement('div');
            editorDiv.className = 'letter-editor-container';
            editorDiv.innerHTML = `
                <div class="letter-editor-header">
                    <div class="letter-editor-title">
                        <span style="color: var(--color-primary); font-size: 1.1rem; margin-right: 0.25rem;">✉</span>
                        <span>${letter.company} &mdash; <span style="font-weight: 400; color: var(--text-secondary);">${letter.role}</span></span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                        <button class="btn btn-secondary btn-sm btn-regenerate">🔄 Regenerate</button>
                        <button class="btn btn-secondary btn-sm btn-copy">📋 Copy</button>
                        <button class="btn btn-secondary btn-sm btn-download">📥 Download</button>
                    </div>
                </div>
                <textarea class="letter-editor-textarea" spellcheck="false">${letter.content}</textarea>
            `;

            const textarea = editorDiv.querySelector('.letter-editor-textarea');
            const copyBtn = editorDiv.querySelector('.btn-copy');
            const downloadBtn = editorDiv.querySelector('.btn-download');
            const regenerateBtn = editorDiv.querySelector('.btn-regenerate');

            // 1. Copy letter content
            copyBtn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(textarea.value);
                    copyBtn.innerHTML = '<span>✓ Copied!</span>';
                    copyBtn.style.color = '#34d399';
                    copyBtn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                    showToast(`Cover letter for ${letter.company} copied to clipboard!`, 'success');
                    setTimeout(() => {
                        copyBtn.innerHTML = '📋 Copy';
                        copyBtn.style.color = '';
                        copyBtn.style.borderColor = '';
                    }, 2000);
                } catch (err) {
                    showToast('Failed to copy text.', 'error');
                }
            });

            // 2. Download letter content
            downloadBtn.addEventListener('click', () => {
                try {
                    const blob = new Blob([textarea.value], { type: 'text/plain;charset=utf-8' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `Cover_Letter_${letter.company.replace(/\s+/g, '_')}.txt`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    showToast('Cover letter downloaded successfully!', 'success');
                } catch (err) {
                    showToast('Failed to download file.', 'error');
                }
            });

            // 3. Regenerate cover letter via API
            regenerateBtn.addEventListener('click', async () => {
                regenerateBtn.setAttribute('disabled', 'true');
                copyBtn.setAttribute('disabled', 'true');
                downloadBtn.setAttribute('disabled', 'true');
                textarea.setAttribute('readonly', 'true');
                const origVal = textarea.value;
                textarea.value = 'Generating cover letter using Gemini, please wait...';

                try {
                    const response = await apiRequest('/results/cover-letter/regenerate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            run_id: runId,
                            company: letter.company,
                            role: letter.role
                        })
                    });
                    textarea.value = response.content;
                    showToast(`Cover letter for ${letter.company} regenerated successfully!`, 'success');
                } catch (err) {
                    showToast(err.message, 'error');
                    textarea.value = origVal; // Restore original content on error
                } finally {
                    regenerateBtn.removeAttribute('disabled');
                    copyBtn.removeAttribute('disabled');
                    downloadBtn.removeAttribute('disabled');
                    textarea.removeAttribute('readonly');
                }
            });

            lettersContainer.appendChild(editorDiv);
        });
    }

    /**
     * Renders Section 4: Metadata details from history
     */
    function renderMetadata(history, runId) {
        const metadata = history.find(run => run.run_id === runId);
        
        if (metadata) {
            runStatusVal.innerHTML = `<span class="badge ${metadata.status === 'success' ? 'badge-secondary' : 'badge-warning'}">${metadata.status.toUpperCase()}</span>`;
            runStartedVal.textContent = formatDate(metadata.started_at);
            runCompletedVal.textContent = formatDate(metadata.completed_at);
        } else {
            runStatusVal.textContent = 'COMPLETED';
            runStartedVal.textContent = 'N/A';
            runCompletedVal.textContent = 'N/A';
            runCompletedVal.textContent = 'N/A';
        }
    }

    function formatDate(dateString) {
        if (!dateString) return 'Pending/Failed';
        try {
            const date = new Date(dateString);
            return date.toLocaleString();
        } catch (e) {
            return dateString;
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initResults);
} else {
    initResults();
}
