// Global Variables
let psychometricQuestions = [];
let nlpQuestions = [];
let psychometricAnswers = [];
let nlpAnswers = [];
let currentQuestion = 0;
let totalQuestions = 0;
let recognition = null;
let particleSystem = null;
let mouseX = 0, mouseY = 0;

// Initialize everything when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    initCustomCursor();
    initParticles();
    initVoiceRecognition();
    loadQuestions();
    createFloatingElements();
    initKeyboardShortcuts();
    initSoundEffects();
});

// Custom Cursor
function initCustomCursor() {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    document.body.appendChild(cursor);
    
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });
    
    document.querySelectorAll('button, .rating-option, .mood-option, .feature-card').forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('custom-cursor-hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('custom-cursor-hover'));
    });
}

// Particle System
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    let particles = [];
    const particleCount = 100;
    
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            radius: Math.random() * 3 + 1,
            speedX: (Math.random() - 0.5) * 0.5,
            speedY: (Math.random() - 0.5) * 0.5,
            color: `rgba(99, 102, 241, ${Math.random() * 0.5})`
        });
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            
            if (p.x < 0) p.x = canvas.width;
            if (p.x > canvas.width) p.x = 0;
            if (p.y < 0) p.y = canvas.height;
            if (p.y > canvas.height) p.y = 0;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Voice Recognition
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = () => {
            showToast('🎤 Listening... Speak now', 'info');
        };
        
        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0].transcript)
                .join('');
            
            const textarea = document.getElementById('nlpResponse');
            if (textarea) {
                textarea.value = transcript;
                saveNlpResponse();
                showTypingIndicator();
                playSound('click');
            }
        };
        
        recognition.onerror = (event) => {
            console.error('Speech error:', event.error);
            showToast('Voice recognition failed. Please type your response.', 'error');
        };
        
        recognition.onend = () => {
            const voiceBtn = document.querySelector('.voice-btn');
            if (voiceBtn) {
                voiceBtn.classList.remove('listening');
                voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            }
        };
    }
}

// Start Voice Input
function startVoiceInput() {
    if (recognition) {
        recognition.start();
        const voiceBtn = event?.target?.closest('.voice-btn');
        if (voiceBtn) {
            voiceBtn.classList.add('listening');
            voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        }
    } else {
        showToast('Voice recognition not supported in your browser', 'warning');
    }
}

// Load Questions from Backend
async function loadQuestions() {
    try {
        const response = await fetch('/api/questions');
        const data = await response.json();
        psychometricQuestions = data.psychometric;
        nlpQuestions = data.nlp;
        totalQuestions = psychometricQuestions.length + nlpQuestions.length;
        document.getElementById('totalSteps').textContent = totalQuestions;
    } catch (error) {
        console.error('Error loading questions:', error);
        showToast('Failed to load questions. Please refresh.', 'error');
    }
}

// Create Floating Elements
function createFloatingElements() {
    setInterval(() => {
        const floatingEmoji = document.createElement('div');
        const emojis = ['🧠', '💭', '✨', '🌟', '💫', '⭐'];
        floatingEmoji.innerHTML = emojis[Math.floor(Math.random() * emojis.length)];
        floatingEmoji.style.cssText = `
            position: fixed;
            left: ${Math.random() * 100}%;
            top: 100%;
            font-size: ${Math.random() * 30 + 20}px;
            opacity: 0;
            pointer-events: none;
            z-index: 999;
            animation: floatUp ${Math.random() * 3 + 2}s ease-out forwards;
        `;
        document.body.appendChild(floatingEmoji);
        
        setTimeout(() => floatingEmoji.remove(), 5000);
    }, 3000);
}

// Add CSS for floating animation
const style = document.createElement('style');
style.textContent = `
    @keyframes floatUp {
        0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
        }
        100% {
            transform: translateY(-100vh) rotate(360deg);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Number keys 1-5 for ratings
        if (currentQuestion < psychometricQuestions.length) {
            if (e.key >= '1' && e.key <= '5') {
                selectRating(parseInt(e.key));
                showToast(`Selected rating: ${e.key}`, 'info');
            }
        }
        
        // Enter to continue
        if (e.key === 'Enter' && document.activeElement?.tagName !== 'TEXTAREA') {
            nextQuestion();
        }
        
        // Escape to go back
        if (e.key === 'Escape') {
            if (confirm('Exit assessment? Progress will be lost.')) {
                location.reload();
            }
        }
    });
}

// Sound Effects
let audioContext = null;

function initSoundEffects() {
    // Initialize audio context on first user interaction
    document.body.addEventListener('click', () => {
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }
    });
}

function playSound(type) {
    if (!audioContext) return;
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    gainNode.gain.value = 0.1;
    
    if (type === 'click') {
        oscillator.frequency.value = 880;
        oscillator.start();
        setTimeout(() => oscillator.stop(), 100);
    } else if (type === 'success') {
        oscillator.frequency.value = 1046.50;
        oscillator.start();
        setTimeout(() => {
            oscillator.frequency.value = 1318.52;
            setTimeout(() => oscillator.stop(), 300);
        }, 100);
    }
}

// Show Toast Notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} me-2"></i>
        ${message}
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Start Assessment
function startAssessment() {
    document.getElementById('welcomeSection').style.display = 'none';
    document.getElementById('assessmentSection').style.display = 'block';
    document.getElementById('assessmentSection').classList.add('fade-in');
    displayQuestion();
    playSound('click');
}

// Display Current Question
function displayQuestion() {
    const isPsychometric = currentQuestion < psychometricQuestions.length;
    const container = document.getElementById('questionContainer');
    const stepInfo = document.getElementById('stepInfo');
    const sectionTitle = document.getElementById('sectionTitle');
    
    if (isPsychometric) {
        sectionTitle.innerHTML = '<i class="fas fa-clipboard-list me-2"></i>Psychometric Assessment';
        stepInfo.innerHTML = '<small>Rate each statement from 1-5 (Keyboard shortcuts: 1-5)</small>';
        const q = psychometricQuestions[currentQuestion];
        const savedAnswer = psychometricAnswers[currentQuestion];
        
        container.innerHTML = `
            <div class="question-card">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <span class="badge bg-primary">Question ${currentQuestion + 1}/${psychometricQuestions.length}</span>
                    <span class="badge bg-info">Rating: ${savedAnswer || 'Not answered'}/5</span>
                </div>
                <h2 class="mb-4">${q.text}</h2>
                <div class="rating-container">
                    ${[1,2,3,4,5].map(num => `
                        <div class="rating-option ${savedAnswer === num ? 'selected' : ''}" onclick="selectRating(${num})">
                            <div class="rating-number">${num}</div>
                            <div class="rating-label">${num === 1 ? 'Never' : num === 2 ? 'Rarely' : num === 3 ? 'Sometimes' : num === 4 ? 'Often' : 'Always'}</div>
                        </div>
                    `).join('')}
                </div>
                <div class="text-center mt-3">
                    <small class="text-muted"><i class="fas fa-keyboard"></i> Press 1-5 on your keyboard</small>
                </div>
            </div>
        `;
    } else {
        sectionTitle.innerHTML = '<i class="fas fa-comment-dots me-2"></i>NLP Emotional Assessment';
        stepInfo.innerHTML = '<small>Share your thoughts in detail (AI analyzes your language)</small>';
        const nlpIndex = currentQuestion - psychometricQuestions.length;
        const q = nlpQuestions[nlpIndex];
        const savedAnswer = nlpAnswers[nlpIndex];
        
        container.innerHTML = `
            <div class="question-card">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <span class="badge bg-primary">Question ${currentQuestion + 1}/${totalQuestions}</span>
                    <span class="badge bg-success">AI Analysis</span>
                </div>
                <h2 class="mb-4">${q.text}</h2>
                <div class="nlp-input-container">
                    <textarea id="nlpResponse" class="nlp-textarea" rows="6" 
                        placeholder="Type your response here... (minimum 15 characters)"
                        oninput="saveNlpResponse(); updateCharCount()">${savedAnswer || ''}</textarea>
                    <button class="voice-btn" onclick="startVoiceInput()" title="Click to speak">
                        <i class="fas fa-microphone"></i>
                    </button>
                </div>
                <div id="typingIndicator" class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="ms-2">AI is analyzing...</span>
                </div>
                <div class="d-flex justify-content-between mt-3">
                    <div id="charCounter">
                        <i class="fas fa-keyboard"></i> <span id="charCount">${(savedAnswer || '').length}</span> characters
                    </div>
                    <div id="wordCounter">
                        <i class="fas fa-language"></i> <span id="wordCount">${(savedAnswer || '').split(' ').length}</span> words
                    </div>
                </div>
                <div class="progress mt-3" style="height: 5px;">
                    <div id="charProgress" class="progress-bar" style="width: ${Math.min(((savedAnswer || '').length / 15) * 100, 100)}%"></div>
                </div>
            </div>
        `;
        updateCharCount();
    }
    
    updateProgress();
    updateMoodSelector();
}

// Update Character Count
function updateCharCount() {
    const textarea = document.getElementById('nlpResponse');
    if (textarea) {
        const length = textarea.value.length;
        const words = textarea.value.trim().split(/\s+/).length;
        document.getElementById('charCount').textContent = length;
        document.getElementById('wordCount').textContent = words;
        
        const progress = Math.min((length / 15) * 100, 100);
        document.getElementById('charProgress').style.width = `${progress}%`;
        
        if (length >= 15) {
            document.getElementById('charProgress').className = 'progress-bar bg-success';
        } else {
            document.getElementById('charProgress').className = 'progress-bar bg-warning';
        }
    }
}

// Select Rating
function selectRating(rating) {
    psychometricAnswers[currentQuestion] = rating;
    updateProgress();
    playSound('click');
    
    // Ripple effect
    const btn = event?.target?.closest('.rating-option');
    if (btn) {
        btn.style.transform = 'scale(0.95)';
        setTimeout(() => btn.style.transform = '', 200);
    }
    
    // Auto-advance after selection
    setTimeout(() => nextQuestion(), 400);
}

// Save NLP Response
function saveNlpResponse() {
    const response = document.getElementById('nlpResponse')?.value || '';
    const nlpIndex = currentQuestion - psychometricQuestions.length;
    if (nlpIndex >= 0) {
        nlpAnswers[nlpIndex] = response;
        updateCharCount();
    }
}

// Show Typing Indicator
function showTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.classList.add('active');
        setTimeout(() => indicator.classList.remove('active'), 1500);
    }
}

// Next Question
function nextQuestion() {
    const isPsychometric = currentQuestion < psychometricQuestions.length;
    
    if (isPsychometric) {
        if (!psychometricAnswers[currentQuestion]) {
            showToast('Please select a rating (1-5) or press a number key', 'warning');
            return;
        }
    } else {
        const nlpIndex = currentQuestion - psychometricQuestions.length;
        const response = document.getElementById('nlpResponse')?.value || '';
        if (response.length < 15) {
            showToast('Please provide a more detailed response (minimum 15 characters)', 'warning');
            return;
        }
        nlpAnswers[nlpIndex] = response;
        showTypingIndicator();
    }
    
    currentQuestion++;
    
    if (currentQuestion < totalQuestions) {
        displayQuestion();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        playSound('click');
    } else {
        submitAssessment();
    }
}

// Update Progress Bar
function updateProgress() {
    const answered = psychometricAnswers.filter(a => a !== undefined).length;
    const percent = ((currentQuestion + 1) / totalQuestions) * 100;
    const progressBar = document.getElementById('progressBar');
    progressBar.style.width = `${percent}%`;
    progressBar.textContent = `${Math.round(percent)}%`;
    document.getElementById('currentStep').textContent = currentQuestion + 1;
}

// Update Mood Selector
function updateMoodSelector() {
    const moodContainer = document.getElementById('moodSelector');
    if (!moodContainer) return;
    
    const moods = [
        { emoji: '😊', label: 'Happy', value: 'happy' },
        { emoji: '😐', label: 'Neutral', value: 'neutral' },
        { emoji: '😔', label: 'Sad', value: 'sad' },
        { emoji: '😟', label: 'Anxious', value: 'anxious' },
        { emoji: '😤', label: 'Stressed', value: 'stressed' },
        { emoji: '😴', label: 'Tired', value: 'tired' },
        { emoji: '🤗', label: 'Calm', value: 'calm' },
        { emoji: '🥰', label: 'Loved', value: 'loved' }
    ];
    
    moodContainer.innerHTML = moods.map(mood => `
        <div class="mood-option" onclick="selectMood('${mood.value}')">
            <div class="mood-emoji">${mood.emoji}</div>
            <div class="mood-label">${mood.label}</div>
        </div>
    `).join('');
}

// Select Mood
function selectMood(mood) {
    document.querySelectorAll('.mood-option').forEach(opt => opt.classList.remove('selected'));
    event.target.closest('.mood-option').classList.add('selected');
    
    // Add mood to current NLP answer
    const textarea = document.getElementById('nlpResponse');
    if (textarea) {
        const currentText = textarea.value;
        textarea.value = `[Feeling: ${mood}] ${currentText}`;
        saveNlpResponse();
        updateCharCount();
    }
    
    playSound('click');
    showToast(`Mood selected: ${mood}`, 'success');
}

//