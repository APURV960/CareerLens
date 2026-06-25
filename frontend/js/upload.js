/**
 * CareerLens Resume Upload Page Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const uploadBtn = document.getElementById('uploadBtn');
    const resultsSection = document.getElementById('resultsSection');
    const resIdVal = document.getElementById('resIdVal');
    const resVerVal = document.getElementById('resVerVal');
    const skillsList = document.getElementById('skillsList');
    const alertContainer = document.getElementById('alertContainer');
    const sessionText = document.getElementById('sessionText');

    let selectedFile = null;

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
        
        // Add close listener
        toast.querySelector('.alert-close').addEventListener('click', () => {
            toast.remove();
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    // Handle Drag & Drop Events
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'dragend', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // Handle click to browse
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // File validation and assignment
    function handleFile(file) {
        if (!file.name.endsWith('.pdf')) {
            showToast('Invalid file format. Only PDF files are supported.', 'error');
            resetFileSelection();
            return;
        }

        selectedFile = file;
        fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.style.display = 'block';
        uploadBtn.removeAttribute('disabled');
        resultsSection.style.display = 'none'; // Clear previous results on new select
    }

    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        fileInfo.textContent = '';
        uploadBtn.setAttribute('disabled', 'true');
    }

    // Handle file upload
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Visual loading state
        uploadBtn.setAttribute('disabled', 'true');
        const originalBtnText = uploadBtn.innerHTML;
        uploadBtn.innerHTML = '<span>⏳ Processing Resume...</span>';

        try {
            const result = await CareerLensAPI.uploadResume(selectedFile);
            console.log("UPLOAD RESPONSE:", result);
            console.log("resume_id:", result.resume_id);
            console.log("version:", result.version);
            
            // Store IDs in browser memory
            localStorage.setItem('resume_id', result.resume_id);
            
            // Populate results details
            resIdVal.textContent = result.resume_id;
            resVerVal.textContent = result.version;
            
            // Render skills
            skillsList.innerHTML = '';
            if (result.skills && result.skills.length > 0) {
                result.skills.forEach(skill => {
                    const badge = document.createElement('span');
                    badge.className = 'badge';
                    badge.textContent = skill;
                    skillsList.appendChild(badge);
                });
            } else {
                skillsList.innerHTML = '<span style="color: var(--text-muted);">No skills detected. We will still search for jobs based on your text content.</span>';
            }

            // Show results section
            resultsSection.style.display = 'block';
            showToast(`Resume uploaded successfully (Version ${result.version})`, 'success');
            
            // Reset upload box
            resetFileSelection();

        } catch (error) {
            showToast(error.message, 'error');
            uploadBtn.removeAttribute('disabled');
        } finally {
            uploadBtn.innerHTML = originalBtnText;
        }
    });
});
