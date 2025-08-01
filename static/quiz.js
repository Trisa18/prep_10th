// Quiz application JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize topic suggestion buttons
    initTopicButtons();
    
    // Initialize quiz form validation
    initFormValidation();
    
    // Initialize quiz transitions
    initQuizTransitions();
    
    // Auto-save functionality for quiz sessions
    initAutoSave();
});

/**
 * Initialize topic suggestion buttons
 */
function initTopicButtons() {
    const topicButtons = document.querySelectorAll('.topic-btn');
    const topicInput = document.getElementById('topic');
    
    topicButtons.forEach(button => {
        button.addEventListener('click', function() {
            const topic = this.getAttribute('data-topic');
            if (topicInput) {
                topicInput.value = topic;
                topicInput.focus();
            }
        });
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loading overlay for quiz submissions
                if (form.action.includes('start_quiz') || form.action.includes('submit_answer')) {
                    showLoadingOverlay();
                }
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Initialize quiz transitions and animations
 */
function initQuizTransitions() {
    const quizCard = document.querySelector('.card');
    if (quizCard && window.location.pathname.includes('/quiz')) {
        quizCard.classList.add('quiz-transition');
    }
    
    // Add click animation to option cards
    const optionCards = document.querySelectorAll('.option-card');
    optionCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove previous selections
            optionCards.forEach(c => c.classList.remove('selected'));
            // Add selection to clicked card
            this.classList.add('selected');
            
            // Check the corresponding radio button
            const radio = this.closest('.form-check').querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }
        });
    });
}

/**
 * Auto-save functionality (for future enhancements)
 */
function initAutoSave() {
    // Store quiz state in localStorage for recovery
    const quizForm = document.querySelector('form[action*="submit_answer"]');
    if (quizForm) {
        const sessionId = extractSessionIdFromPage();
        if (sessionId) {
            // Save quiz state periodically
            setInterval(() => {
                saveQuizState(sessionId);
            }, 30000); // Save every 30 seconds
        }
    }
}

/**
 * Show loading overlay
 */
function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    } else {
        // Create loading overlay if it doesn't exist
        const loadingHTML = `
            <div id="loadingOverlay" class="loading-overlay">
                <div class="text-center">
                    <div class="spinner-border text-light" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2 text-light">Generating questions...</p>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', loadingHTML);
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

/**
 * Load performance chart for results page
 */
function loadPerformanceChart(sessionId) {
    fetch(`/api/performance_data/${sessionId}`)
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('performanceChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            data: data.data,
                            backgroundColor: data.backgroundColor,
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 20,
                                    usePointStyle: true
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const label = context.label || '';
                                        const value = context.parsed;
                                        const total = data.total_questions;
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `${label}: ${value} (${percentage}%)`;
                                    }
                                }
                            }
                        },
                        cutout: '60%'
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error loading performance chart:', error);
        });
}

/**
 * Extract session ID from current page (utility function)
 */
function extractSessionIdFromPage() {
    const url = window.location.pathname;
    const matches = url.match(/\/results\/(\d+)/);
    return matches ? matches[1] : null;
}

/**
 * Save quiz state to localStorage
 */
function saveQuizState(sessionId) {
    try {
        const selectedAnswer = document.querySelector('input[name="answer"]:checked');
        if (selectedAnswer) {
            const state = {
                sessionId: sessionId,
                answer: selectedAnswer.value,
                timestamp: new Date().toISOString()
            };
            localStorage.setItem(`quiz_state_${sessionId}`, JSON.stringify(state));
        }
    } catch (error) {
        console.error('Error saving quiz state:', error);
    }
}

/**
 * Restore quiz state from localStorage
 */
function restoreQuizState(sessionId) {
    try {
        const savedState = localStorage.getItem(`quiz_state_${sessionId}`);
        if (savedState) {
            const state = JSON.parse(savedState);
            const radioButton = document.querySelector(`input[name="answer"][value="${state.answer}"]`);
            if (radioButton) {
                radioButton.checked = true;
                radioButton.closest('.form-check').querySelector('.option-card').classList.add('selected');
            }
        }
    } catch (error) {
        console.error('Error restoring quiz state:', error);
    }
}

/**
 * Timer functionality for quiz sessions
 */
function startQuizTimer() {
    const startTime = new Date();
    const timerElement = document.getElementById('quizTimer');
    
    if (timerElement) {
        setInterval(() => {
            const currentTime = new Date();
            const elapsed = Math.floor((currentTime - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
}

/**
 * Keyboard navigation for quiz
 */
document.addEventListener('keydown', function(event) {
    if (window.location.pathname.includes('/quiz')) {
        // Allow A, B, C, D keys to select options
        if (['KeyA', 'KeyB', 'KeyC', 'KeyD'].includes(event.code)) {
            const optionLetter = event.code.replace('Key', '');
            const radioButton = document.querySelector(`input[name="answer"][value="${optionLetter}"]`);
            if (radioButton) {
                radioButton.checked = true;
                radioButton.closest('.form-check').querySelector('.option-card').click();
            }
        }
        
        // Enter key to submit
        if (event.code === 'Enter' && !event.shiftKey) {
            const submitButton = document.querySelector('button[type="submit"]');
            if (submitButton && document.querySelector('input[name="answer"]:checked')) {
                submitButton.click();
            }
        }
    }
});

/**
 * Smooth scrolling for better UX
 */
function smoothScrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Auto-scroll to top on page transitions
window.addEventListener('beforeunload', function() {
    smoothScrollToTop();
});

/**
 * Enhanced error handling
 */
window.addEventListener('error', function(event) {
    console.error('JavaScript error:', event.error);
    hideLoadingOverlay();
});

/**
 * Network status monitoring
 */
window.addEventListener('online', function() {
    const offlineAlert = document.querySelector('.offline-alert');
    if (offlineAlert) {
        offlineAlert.remove();
    }
});

window.addEventListener('offline', function() {
    const alertHTML = `
        <div class="alert alert-warning offline-alert position-fixed top-0 start-50 translate-middle-x mt-3" style="z-index: 10000;">
            <i class="fas fa-wifi-slash me-2"></i>You are currently offline. Please check your connection.
        </div>
    `;
    document.body.insertAdjacentHTML('afterbegin', alertHTML);
});
