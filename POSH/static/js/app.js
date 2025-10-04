// POSH Video Generation System - Frontend JavaScript
class POSHVideoApp {
    constructor() {
        this.currentSessionId = null;
        this.pollingInterval = null;
        this.examples = {};
        
        this.initializeApp();
        this.loadExamples();
    }

    initializeApp() {
        // Get DOM elements
        this.elements = {
            exampleSelect: document.getElementById('example-select'),
            scenarioInput: document.getElementById('scenario-input'),
            generateBtn: document.getElementById('generate-btn'),
            retryBtn: document.getElementById('retry-btn'),
            
            // Sections
            inputSection: document.getElementById('input-section'),
            processingSection: document.getElementById('processing-section'),
            scenarioSection: document.getElementById('scenario-section'),
            videosSection: document.getElementById('videos-section'),
            errorSection: document.getElementById('error-section'),
            
            // Progress elements
            progressFill: document.getElementById('progress-fill'),
            progressText: document.getElementById('progress-text'),
            currentStep: document.getElementById('current-step'),
            
            // Content elements
            scenarioDetails: document.getElementById('scenario-details'),
            videoSummary: document.getElementById('video-summary'),
            videoList: document.getElementById('video-list'),
            errorMessage: document.getElementById('error-message')
        };

        // Add event listeners
        this.elements.exampleSelect.addEventListener('change', () => this.handleExampleChange());
        this.elements.generateBtn.addEventListener('click', () => this.handleGenerate());
        this.elements.retryBtn.addEventListener('click', () => this.handleRetry());

        // Add input validation
        this.elements.scenarioInput.addEventListener('input', () => this.validateInput());
    }

    async loadExamples() {
        try {
            const response = await fetch('/api/examples');
            this.examples = await response.json();
        } catch (error) {
            console.error('Failed to load examples:', error);
        }
    }

    handleExampleChange() {
        const selectedExample = this.elements.exampleSelect.value;
        if (selectedExample && this.examples[selectedExample]) {
            this.elements.scenarioInput.value = this.examples[selectedExample];
            this.validateInput();
        }
    }

    validateInput() {
        const text = this.elements.scenarioInput.value.trim();
        const isValid = text.length >= 50;
        
        this.elements.generateBtn.disabled = !isValid;
        
        if (text.length > 0 && text.length < 50) {
            this.elements.generateBtn.textContent = `🚀 Generate Videos (${text.length}/50 characters minimum)`;
        } else {
            this.elements.generateBtn.textContent = '🚀 Generate POSH Training Videos';
        }
    }

    async handleGenerate() {
        const scenarioText = this.elements.scenarioInput.value.trim();
        
        if (!scenarioText || scenarioText.length < 50) {
            this.showError('Please provide a detailed scenario (at least 50 characters).');
            return;
        }

        try {
            this.showProcessing();
            
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    scenario_text: scenarioText
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start generation');
            }

            const result = await response.json();
            this.currentSessionId = result.session_id;
            
            // Start polling for status
            this.startPolling();
            
        } catch (error) {
            console.error('Generation error:', error);
            this.showError(error.message);
        }
    }

    startPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        this.pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/status/${this.currentSessionId}`);
                if (!response.ok) {
                    throw new Error('Failed to get status');
                }

                const status = await response.json();
                this.updateProgress(status);

                if (status.status === 'completed') {
                    clearInterval(this.pollingInterval);
                    this.showResults(status);
                } else if (status.status === 'error') {
                    clearInterval(this.pollingInterval);
                    this.showError(status.error_message);
                }
                
            } catch (error) {
                console.error('Polling error:', error);
                clearInterval(this.pollingInterval);
                this.showError('Failed to get generation status');
            }
        }, 2000); // Poll every 2 seconds
    }

    updateProgress(status) {
        const progressPercent = Math.round(status.progress * 100);
        
        this.elements.progressFill.style.width = `${progressPercent}%`;
        this.elements.progressText.textContent = `${progressPercent}% - ${status.current_step}`;
        this.elements.currentStep.textContent = status.current_step;
    }

    showProcessing() {
        this.hideAllSections();
        this.elements.processingSection.style.display = 'block';
        
        // Reset progress
        this.elements.progressFill.style.width = '0%';
        this.elements.progressText.textContent = '0% - Starting...';
        this.elements.currentStep.textContent = 'Initializing...';
    }

    showResults(status) {
        this.hideAllSections();
        
        // Show scenario breakdown if available
        if (status.processed_scenario) {
            this.displayScenarioBreakdown(status.processed_scenario);
            this.elements.scenarioSection.style.display = 'block';
        }

        // Show videos if available
        if (status.video_summary) {
            this.displayVideoResults(status.video_summary);
            this.elements.videosSection.style.display = 'block';
        }
    }

    displayScenarioBreakdown(scenario) {
        const html = `
            <div class="scenario-overview">
                <div class="scenario-info">
                    <h3>🎭 ${scenario.title}</h3>
                    <p>${scenario.description}</p>
                </div>
                <div class="scenario-metrics">
                    <div class="metric">
                        <div class="metric-value">${scenario.scenes.length}</div>
                        <div class="metric-label">Total Scenes</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">${scenario.total_duration}s</div>
                        <div class="metric-label">Total Duration</div>
                    </div>
                </div>
            </div>

            <div class="learning-objectives">
                <h3>🎯 Learning Objectives</h3>
                <ol>
                    ${scenario.learning_objectives.map(obj => `<li>${obj}</li>`).join('')}
                </ol>
            </div>

            <h3>🎬 Scene Breakdown</h3>
            ${scenario.scenes.map(scene => `
                <div class="scene-card">
                    <div class="scene-header">
                        <div class="scene-title">Scene ${scene.scene_number}: ${scene.setting}</div>
                        <div class="scene-duration">${scene.duration_seconds}s</div>
                    </div>
                    <div class="scene-details">
                        <div class="scene-content">
                            <h4>Visual Description:</h4>
                            <p>${scene.visual_description}</p>
                            <h4>Dialogue:</h4>
                            <p>"${scene.audio_script.dialogue}"</p>
                            ${scene.audio_script.sound_effects ? `
                                <h4>Sound Effects:</h4>
                                <p>${scene.audio_script.sound_effects}</p>
                            ` : ''}
                            ${scene.continuity_notes ? `
                                <h4>Continuity Notes:</h4>
                                <p>${scene.continuity_notes}</p>
                            ` : ''}
                        </div>
                        <div class="scene-meta">
                            <p><strong>Characters:</strong> ${scene.characters.join(', ')}</p>
                            <p><strong>Tone:</strong> ${scene.audio_script.tone}</p>
                            ${scene.audio_script.background_narration ? `
                                <p><strong>Narration:</strong> ${scene.audio_script.background_narration}</p>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('')}
        `;

        this.elements.scenarioDetails.innerHTML = html;
    }

    displayVideoResults(videoSummary) {
        // Summary cards
        const summaryHtml = `
            <div class="video-summary">
                <div class="summary-card">
                    <div class="summary-number">${videoSummary.successful_scenes}</div>
                    <div class="summary-label">Successfully Generated</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${videoSummary.total_scenes}</div>
                    <div class="summary-label">Total Scenes</div>
                </div>
                <div class="summary-card">
                    <div class="summary-number">${videoSummary.failed_scenes || 0}</div>
                    <div class="summary-label">Failed</div>
                </div>
            </div>
        `;

        // Video list
        const videosHtml = videoSummary.videos
            .filter(video => video.file_info && video.file_info.exists)
            .map(video => `
                <div class="video-container">
                    <h3>Scene ${video.scene_number}: ${video.setting}</h3>
                    <div class="video-player-container">
                        <div>
                            <video controls preload="metadata">
                                <source src="/api/video/${this.getVideoFilename(video.video_path)}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        <div class="video-info">
                            <h4>Characters:</h4>
                            <p>${video.characters.join(', ')}</p>
                            <h4>Dialogue:</h4>
                            <p>"${video.dialogue}"</p>
                            ${video.file_info.file_size_mb ? `
                                <p><strong>File Size:</strong> ${video.file_info.file_size_mb.toFixed(1)} MB</p>
                            ` : ''}
                            ${video.generation_time ? `
                                <p><strong>Generation Time:</strong> ${video.generation_time.toFixed(1)}s</p>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `).join('');

        this.elements.videoSummary.innerHTML = summaryHtml;
        this.elements.videoList.innerHTML = videosHtml;
    }

    getVideoFilename(videoPath) {
        return videoPath.split(/[/\\]/).pop();
    }

    showError(message) {
        this.hideAllSections();
        this.elements.errorMessage.textContent = message;
        this.elements.errorSection.style.display = 'block';
        
        // Stop polling if active
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    handleRetry() {
        this.hideAllSections();
        this.elements.inputSection.style.display = 'block';
        this.currentSessionId = null;
    }

    hideAllSections() {
        const sections = [
            this.elements.processingSection,
            this.elements.scenarioSection,
            this.elements.videosSection,
            this.elements.errorSection
        ];
        
        sections.forEach(section => {
            section.style.display = 'none';
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new POSHVideoApp();
});

// Add some utility functions for better UX
window.addEventListener('beforeunload', (event) => {
    // Warn user if generation is in progress
    const app = window.poshApp;
    if (app && app.pollingInterval) {
        event.preventDefault();
        event.returnValue = 'Video generation is in progress. Are you sure you want to leave?';
        return event.returnValue;
    }
});

// Store app instance globally for debugging
window.addEventListener('load', () => {
    window.poshApp = new POSHVideoApp();
});

