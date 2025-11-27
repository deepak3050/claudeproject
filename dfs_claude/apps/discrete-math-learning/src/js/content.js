// Truth Tables Data
const truthTables = {
    and: {
        name: 'AND (∧)',
        columns: ['p', 'q', 'p ∧ q'],
        rows: [
            ['T', 'T', 'T'],
            ['T', 'F', 'F'],
            ['F', 'T', 'F'],
            ['F', 'F', 'F']
        ]
    },
    or: {
        name: 'OR (∨)',
        columns: ['p', 'q', 'p ∨ q'],
        rows: [
            ['T', 'T', 'T'],
            ['T', 'F', 'T'],
            ['F', 'T', 'T'],
            ['F', 'F', 'F']
        ]
    },
    not: {
        name: 'NOT (¬)',
        columns: ['p', '¬p'],
        rows: [
            ['T', 'F'],
            ['F', 'T']
        ]
    },
    implies: {
        name: 'IMPLIES (→)',
        columns: ['p', 'q', 'p → q'],
        rows: [
            ['T', 'T', 'T'],
            ['T', 'F', 'F'],
            ['F', 'T', 'T'],
            ['F', 'F', 'T']
        ]
    }
};

// Show truth table
function showTruthTable(operator) {
    const display = document.getElementById('truth-table-display');
    const nameElement = document.getElementById('operator-name');
    const contentElement = document.getElementById('truth-table-content');

    const table = truthTables[operator];

    nameElement.textContent = table.name;

    let html = '<table class="truth-table"><thead><tr>';
    table.columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';

    table.rows.forEach(row => {
        html += '<tr>';
        row.forEach(cell => {
            html += `<td>${cell}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';

    contentElement.innerHTML = html;
    display.style.display = 'block';

    // Smooth scroll to truth table
    display.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Interactive Logic Gate
function updateLogicGate() {
    const propA = document.getElementById('propA');
    const propB = document.getElementById('propB');
    const operation = document.getElementById('operation');
    const result = document.getElementById('logic-result');

    if (!propA || !propB || !operation || !result) return;

    const a = propA.checked;
    const b = propB.checked;
    const op = operation.value;

    let output;
    switch(op) {
        case 'and':
            output = a && b;
            break;
        case 'or':
            output = a || b;
            break;
        case 'implies':
            output = !a || b;
            break;
        default:
            output = false;
    }

    result.textContent = output.toString();
    result.style.color = output ? '#4ade80' : '#f87171';
}

// Quiz functionality
const correctAnswers = {
    1: 'false',
    2: 'true'
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
            if (btn.textContent.toLowerCase().includes(correctAnswers[questionNum]) ||
                correctAnswers[questionNum] === 'true' && btn.textContent.includes('must be True')) {
                btn.classList.add('correct');
            }
        });
    }
}

// Progress tracking
function updateProgress(increment) {
    const currentProgress = parseInt(localStorage.getItem('progress_logic') || 0);
    const newProgress = Math.min(currentProgress + increment, 100);
    localStorage.setItem('progress_logic', newProgress);

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

    localStorage.setItem('progress_logic', progress);

    const progressText = document.getElementById('progress-text');
    if (progressText) {
        progressText.textContent = `Progress: ${progress}%`;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Interactive logic gate listeners
    const propA = document.getElementById('propA');
    const propB = document.getElementById('propB');
    const operation = document.getElementById('operation');

    if (propA && propB && operation) {
        propA.addEventListener('change', updateLogicGate);
        propB.addEventListener('change', updateLogicGate);
        operation.addEventListener('change', updateLogicGate);
        updateLogicGate(); // Initial update
    }

    // Track scroll progress
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(calculateScrollProgress, 100);
    });

    // Load initial progress
    const savedProgress = localStorage.getItem('progress_logic') || 0;
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
