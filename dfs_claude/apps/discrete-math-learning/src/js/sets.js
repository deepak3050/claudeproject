// Quiz functionality for Sets & Set Operations
const correctAnswers = {
    1: 'a',
    2: 'a',
    3: 'a',
    4: 'a'
};

function checkAnswer(questionNum, answer, button) {
    const buttons = button.parentElement.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.disabled = true;
    });

    if (answer === correctAnswers[questionNum]) {
        button.classList.add('correct');
        updateProgress(10);
    } else {
        button.classList.add('incorrect');
        // Show correct answer
        buttons.forEach(btn => {
            const btnAnswer = btn.getAttribute('onclick').match(/'([^']+)'/)[1];
            if (btnAnswer === correctAnswers[questionNum]) {
                btn.classList.add('correct');
            }
        });
    }
}

// Progress tracking
function updateProgress(increment) {
    const currentProgress = parseInt(localStorage.getItem('progress_sets') || 0);
    const newProgress = Math.min(currentProgress + increment, 100);
    localStorage.setItem('progress_sets', newProgress);

    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `Progress: ${newProgress}%`;
    }
}

// Scroll progress
function calculateScrollProgress() {
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const scrollTop = window.scrollY;

    const scrollPercentage = (scrollTop / (documentHeight - windowHeight)) * 100;
    const progress = Math.min(Math.round(scrollPercentage), 100);

    localStorage.setItem('progress_sets', progress);

    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `Progress: ${progress}%`;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Track scroll progress
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(calculateScrollProgress, 100);
    });

    // Load initial progress
    const savedProgress = localStorage.getItem('progress_sets') || 0;
    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `Progress: ${savedProgress}%`;
    }

    // Animate sections on scroll
    const sections = document.querySelectorAll('.content-section');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    sections.forEach(section => {
        observer.observe(section);
    });
});
