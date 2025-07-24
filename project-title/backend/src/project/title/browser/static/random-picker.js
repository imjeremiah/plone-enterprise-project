/**
 * Random Student Picker JavaScript for Classroom Management
 * 
 * Handles spinner animation, AJAX communication with backend,
 * and real-time display of fairness statistics.
 */

class RandomStudentPicker {
    constructor() {
        this.config = null;
        this.students = [];
        this.isSpinning = false;
        this.pickerHistory = {};
        this.sessionPicks = [];
        
        // DOM elements
        this.spinButton = null;
        this.resetButton = null;
        this.pickerWheel = null;
        this.wheelContent = null;
        this.selectionModal = null;
        this.loadingOverlay = null;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initialize the picker interface
     */
    init() {
        try {
            this.loadConfig();
            this.initializeElements();
            this.setupEventListeners();
            this.loadPickerData();
            this.renderWheel();
            
            console.log('Random Student Picker initialized successfully');
        } catch (error) {
            console.error('Failed to initialize Random Student Picker:', error);
            this.showError('Failed to initialize picker. Please refresh the page.');
        }
    }

    /**
     * Load configuration from the page
     */
    loadConfig() {
        const configElement = document.getElementById('picker-config');
        if (configElement) {
            this.config = JSON.parse(configElement.textContent);
            this.students = this.config.students || [];
        } else {
            console.warn('Picker configuration not found, using default students');
            this.config = { apiUrl: window.location.pathname };
            this.students = [
                "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown",
                "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore",
                "Ivy Taylor", "Jack Anderson", "Kate Thomas", "Liam Jackson",
                "Maya White", "Noah Harris", "Olivia Martin", "Paul Thompson"
            ];
        }
        console.log('Loaded students:', this.students);
    }

    /**
     * Initialize DOM element references
     */
    initializeElements() {
        this.spinButton = document.getElementById('spin-button');
        this.resetButton = document.getElementById('reset-button');
        this.pickerWheel = document.getElementById('picker-wheel');
        this.wheelContent = document.getElementById('wheel-content');
        this.selectionModal = document.getElementById('selection-modal');
        this.loadingOverlay = document.getElementById('loading-overlay');

        if (!this.spinButton || !this.pickerWheel) {
            throw new Error('Required DOM elements not found');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Spin button
        this.spinButton.addEventListener('click', () => this.spinWheel());
        
        // Reset button
        if (this.resetButton) {
            this.resetButton.addEventListener('click', () => this.resetHistory());
        }
        
        // Modal close events
        const closeModal = document.getElementById('close-modal');
        const doneButton = document.getElementById('done-picking');
        const pickAnotherButton = document.getElementById('pick-another');
        
        if (closeModal) {
            closeModal.addEventListener('click', () => this.hideModal());
        }
        if (doneButton) {
            doneButton.addEventListener('click', () => this.hideModal());
        }
        if (pickAnotherButton) {
            pickAnotherButton.addEventListener('click', () => {
                this.hideModal();
                setTimeout(() => this.spinWheel(), 500);
            });
        }

        // Click outside modal to close
        if (this.selectionModal) {
            this.selectionModal.addEventListener('click', (e) => {
                if (e.target === this.selectionModal) {
                    this.hideModal();
                }
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.selectionModal.classList.contains('hidden')) {
                this.hideModal();
            }
            if (e.key === ' ' && !this.isSpinning) {  // Spacebar to spin
                e.preventDefault();
                this.spinWheel();
            }
        });
    }

    /**
     * Render the spinning wheel with student names
     */
    renderWheel() {
        if (!this.wheelContent) return;
        
        console.log('Rendering wheel with students:', this.students);

        // Clear existing content
        this.wheelContent.innerHTML = '';

        // If no students, show message
        if (!this.students.length) {
            const message = document.createElement('div');
            message.className = 'no-students-message';
            message.textContent = 'No students available';
            message.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #666;
                font-size: 14px;
                text-align: center;
            `;
            this.wheelContent.appendChild(message);
            return;
        }

        // Calculate angle per student
        const anglePerStudent = 360 / this.students.length;
        const wheelRadius = 175; // Half of wheel width (350px / 2)

        // Create student segments
        this.students.forEach((student, index) => {
            const segment = document.createElement('div');
            segment.className = 'student-segment';
            segment.textContent = this.formatStudentName(student);
            
            // Calculate position around circumference
            const angle = (anglePerStudent * index) * (Math.PI / 180); // Convert to radians
            const x = Math.cos(angle - Math.PI/2) * (wheelRadius - 60); // -60 to place text inside wheel
            const y = Math.sin(angle - Math.PI/2) * (wheelRadius - 60);
            
            // Position the segment
            segment.style.left = `calc(50% + ${x}px)`;
            segment.style.top = `calc(50% + ${y}px)`;
            
            // Rotate text to be readable (perpendicular to radius)
            let rotation = anglePerStudent * index;
            if (rotation > 90 && rotation < 270) {
                // Flip text for better readability on the bottom half
                rotation += 180;
            }
            
            segment.style.transform = `translate(-50%, -50%) rotate(${rotation}deg)`;
            segment.style.zIndex = this.students.length - index;
            
            this.wheelContent.appendChild(segment);
        });
    }

    /**
     * Format student name for display
     */
    formatStudentName(fullName) {
        const nameParts = fullName.trim().split(' ');
        if (nameParts.length === 1) {
            return nameParts[0];
        }
        
        const firstName = nameParts[0];
        const lastName = nameParts[nameParts.length - 1];
        const lastInitial = lastName.charAt(0).toUpperCase();
        
        return `${firstName} ${lastInitial}.`;
    }

    /**
     * Spin the wheel and select a student
     */
    async spinWheel() {
        if (this.isSpinning || !this.students.length) return;

        this.isSpinning = true;
        this.spinButton.disabled = true;
        this.spinButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Spinning...';

        try {
            // Show loading
            this.showLoading();

            // Visual spinning animation
            const spins = 3 + Math.random() * 2; // 3-5 full rotations
            const finalAngle = Math.random() * 360;
            const totalRotation = spins * 360 + finalAngle;

            // Set CSS custom property for animation
            this.pickerWheel.style.setProperty('--final-rotation', `${finalAngle}deg`);
            this.pickerWheel.classList.add('spinning');

            // Wait for animation to complete (4 seconds)
            await this.sleep(4000);

            // Make API call to backend
            const result = await this.pickStudentFromBackend();

            if (result.success) {
                await this.sleep(500); // Brief pause for effect
                this.hideLoading();
                this.showSelectionResult(result);
                this.updateStatistics();
            } else {
                throw new Error(result.error || 'Selection failed');
            }

        } catch (error) {
            console.error('Spinning failed:', error);
            this.hideLoading();
            this.showError('Failed to select student. Please try again.');
        } finally {
            this.isSpinning = false;
            this.spinButton.disabled = false;
            this.spinButton.innerHTML = '<i class="fas fa-play"></i> Pick a Student';
            this.pickerWheel.classList.remove('spinning');
        }
    }

    /**
     * Make API call to backend for student selection
     */
    async pickStudentFromBackend() {
        const response = await fetch(`${this.config.apiUrl}/@@pick-student`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    }

    /**
     * Load picker data and statistics from backend
     */
    async loadPickerData() {
        try {
            const response = await fetch(`${this.config.apiUrl}/@@random-picker?ajax_data=1`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                credentials: 'include'
            });

            if (response.ok) {
                const data = await response.json();
                this.pickerHistory = data.pick_history || {};
                this.sessionPicks = data.session_picks || [];
                this.updateStatistics();
            }
        } catch (error) {
            console.warn('Failed to load picker data:', error);
        }
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        // Update basic stats
        const totalStudentsEl = document.getElementById('total-students');
        const fairnessScoreEl = document.getElementById('fairness-score');
        const todayPicksEl = document.getElementById('today-picks');

        if (totalStudentsEl) {
            totalStudentsEl.textContent = this.students.length;
        }

        const fairnessScore = this.calculateFairnessScore();
        if (fairnessScoreEl) {
            fairnessScoreEl.textContent = `${fairnessScore}%`;
            fairnessScoreEl.className = 'stat-value ' + this.getFairnessClass(fairnessScore);
        }

        const totalPicks = Object.values(this.pickerHistory).reduce((sum, student) => sum + (student.count || 0), 0);
        if (todayPicksEl) {
            todayPicksEl.textContent = totalPicks;
        }

        // Update recent picks
        this.updateRecentPicks();
        
        // Update history table
        this.updateHistoryTable();
    }

    /**
     * Calculate fairness score
     */
    calculateFairnessScore() {
        if (!Object.keys(this.pickerHistory).length) {
            return 100;
        }

        const picks = Object.values(this.pickerHistory).map(student => student.count || 0);
        if (picks.every(p => p === 0)) {
            return 100;
        }

        const avg = picks.reduce((sum, p) => sum + p, 0) / picks.length;
        const variance = picks.reduce((sum, p) => sum + Math.pow(p - avg, 2), 0) / picks.length;
        
        // Convert to fairness score (lower variance = higher fairness)
        const maxVariance = Math.pow(avg, 2);
        const fairness = maxVariance > 0 ? 100 * (1 - Math.min(variance / maxVariance, 1)) : 100;
        
        return Math.round(fairness);
    }

    /**
     * Get CSS class for fairness score
     */
    getFairnessClass(score) {
        if (score >= 80) return 'fairness-excellent';
        if (score >= 60) return 'fairness-good';
        if (score >= 40) return 'fairness-fair';
        return 'fairness-poor';
    }

    /**
     * Update recent picks display
     */
    updateRecentPicks() {
        const recentPicksList = document.getElementById('recent-picks');
        if (!recentPicksList) return;

        recentPicksList.innerHTML = '';

        // Get recent picks from session and history
        const recentPicks = this.sessionPicks.slice(-5).reverse();

        if (recentPicks.length === 0) {
            const li = document.createElement('li');
            li.textContent = 'No picks yet today';
            li.style.fontStyle = 'italic';
            li.style.color = '#6c757d';
            recentPicksList.appendChild(li);
            return;
        }

        recentPicks.forEach((pick, index) => {
            const li = document.createElement('li');
            const time = new Date(pick.timestamp).toLocaleTimeString([], {
                hour: '2-digit',
                minute: '2-digit'
            });
            li.innerHTML = `
                <span>${pick.student}</span>
                <span>${time}</span>
            `;
            if (index === 0) {
                li.style.fontWeight = 'bold';
            }
            recentPicksList.appendChild(li);
        });
    }

    /**
     * Update history table
     */
    updateHistoryTable() {
        const historyTable = document.getElementById('history-table');
        if (!historyTable) return;

        const tbody = historyTable.querySelector('tbody');
        tbody.innerHTML = '';

        if (Object.keys(this.pickerHistory).length === 0) {
            const row = tbody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = 3;
            cell.textContent = 'No selection history yet';
            cell.style.textAlign = 'center';
            cell.style.fontStyle = 'italic';
            cell.style.color = '#6c757d';
            return;
        }

        // Sort students by pick count (ascending) for fairness visibility
        const sortedStudents = Object.entries(this.pickerHistory)
            .sort(([,a], [,b]) => (a.count || 0) - (b.count || 0));

        sortedStudents.forEach(([student, data]) => {
            const row = tbody.insertRow();
            
            // Student name
            const nameCell = row.insertCell();
            nameCell.textContent = student;
            
            // Pick count
            const countCell = row.insertCell();
            countCell.textContent = data.count || 0;
            
            // Last picked
            const lastCell = row.insertCell();
            if (data.last_picked) {
                const lastDate = new Date(data.last_picked * 1000);
                lastCell.textContent = lastDate.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } else {
                lastCell.textContent = 'Never';
                lastCell.style.fontStyle = 'italic';
                lastCell.style.color = '#6c757d';
            }

            // Highlight students who haven't been picked
            if (!data.count || data.count === 0) {
                row.style.backgroundColor = '#fff3cd';
                row.style.borderLeft = '3px solid #ffc107';
            }
        });
    }

    /**
     * Show selection result modal
     */
    showSelectionResult(result) {
        const studentNameEl = document.getElementById('selected-student-name');
        const selectionTimeEl = document.getElementById('selection-time');
        const modalFairnessEl = document.getElementById('modal-fairness-score');

        if (studentNameEl) {
            studentNameEl.textContent = result.selected;
        }
        if (selectionTimeEl) {
            const time = new Date(result.timestamp).toLocaleTimeString();
            selectionTimeEl.textContent = `Selected at: ${time}`;
        }
        if (modalFairnessEl) {
            modalFairnessEl.textContent = `${result.fairness_score}%`;
        }

        // Add to session picks
        this.sessionPicks.push({
            student: result.selected,
            timestamp: result.timestamp
        });

        // Play success sound (if available)
        this.playSound('success');

        // Show modal
        this.selectionModal.classList.remove('hidden');
        
        // Focus management for accessibility
        const closeButton = document.getElementById('close-modal');
        if (closeButton) {
            closeButton.focus();
        }
    }

    /**
     * Hide selection modal
     */
    hideModal() {
        if (this.selectionModal) {
            this.selectionModal.classList.add('hidden');
            this.spinButton.focus(); // Return focus to spin button
        }
    }

    /**
     * Show loading overlay
     */
    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.remove('hidden');
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('hidden');
        }
    }

    /**
     * Reset picking history
     */
    async resetHistory() {
        if (!confirm('Are you sure you want to reset all picking history for today? This cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`${this.config.apiUrl}/@@random-picker`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ action: 'reset_history' }),
                credentials: 'include'
            });

            if (response.ok) {
                this.pickerHistory = {};
                this.sessionPicks = [];
                this.updateStatistics();
                this.showMessage('History reset successfully!', 'success');
            } else {
                throw new Error('Failed to reset history');
            }
        } catch (error) {
            console.error('Reset failed:', error);
            this.showError('Failed to reset history. Please try again.');
        }
    }

    /**
     * Play sound effect
     */
    playSound(type) {
        try {
            const audio = new Audio(`/++resource++project.title/sounds/${type}.mp3`);
            audio.volume = 0.3;
            audio.play().catch(e => {
                console.log('Audio play failed (this is normal on some browsers):', e.message);
            });
        } catch (error) {
            // Sound is optional, don't break functionality
            console.log('Sound effect not available:', error.message);
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showMessage(message, 'error');
    }

    /**
     * Show message to user
     */
    showMessage(message, type = 'info') {
        // Create simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            backgroundColor: type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#17a2b8',
            zIndex: '1001',
            animation: 'toast-appear 0.3s ease'
        });

        document.body.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'toast-disappear 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    /**
     * Utility: Sleep function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// CSS for toast notifications
const toastStyles = `
@keyframes toast-appear {
    0% { opacity: 0; transform: translateX(100%); }
    100% { opacity: 1; transform: translateX(0); }
}

@keyframes toast-disappear {
    0% { opacity: 1; transform: translateX(0); }
    100% { opacity: 0; transform: translateX(100%); }
}

.stat-value.fairness-excellent { color: #28a745; }
.stat-value.fairness-good { color: #17a2b8; }
.stat-value.fairness-fair { color: #ffc107; }
.stat-value.fairness-poor { color: #dc3545; }
`;

// Inject toast styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);

// Initialize the picker
new RandomStudentPicker(); 