// Navigation function
function navigateTo(page) {
    window.location.href = page;
}

// Load progress from localStorage
function loadProgress() {
    const topics = ['logic', 'sets', 'counting', 'graphs', 'recurrence', 'algorithms', 'number-theory', 'probability'];

    topics.forEach(topic => {
        const progress = localStorage.getItem(`progress_${topic}`) || 0;
        const card = document.querySelector(`[data-topic="${topic}"]`);
        if (card) {
            const progressBar = card.querySelector('.progress');
            if (progressBar) {
                setTimeout(() => {
                    progressBar.style.width = `${progress}%`;
                }, 500);
            }
        }
    });
}

// Save progress
function saveProgress(topic, percentage) {
    localStorage.setItem(`progress_${topic}`, percentage);
}

// Add hover effects
document.addEventListener('DOMContentLoaded', () => {
    loadProgress();

    // Add interactive card effects
    const cards = document.querySelectorAll('.topic-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.borderLeft = '5px solid #667eea';
        });

        card.addEventListener('mouseleave', function() {
            this.style.borderLeft = 'none';
        });
    });
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all topic cards
document.querySelectorAll('.topic-card').forEach(card => {
    observer.observe(card);
});
