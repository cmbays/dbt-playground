// Japanese Language Learning App - Shared JavaScript
// This file contains all common functions used across scenario pages

// Track answered quizzes and score
let answeredQuizzes = new Set();
let score = 0;
let totalAnswered = 0;

// ============================================================================
// NAVIGATION FUNCTIONS
// ============================================================================

/**
 * Show a specific scenario card and hide others
 */
function showScenario(id) {
    speechSynthesis.cancel();
    document.querySelectorAll('.scenario-card').forEach(c => c.classList.add('hidden'));
    const target = document.getElementById(id);
    if (target) {
        target.classList.remove('hidden');
    }
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

/**
 * Show a specific modality (dialogue, story, manga, quiz, tips) within a scenario
 */
function showModality(scenario, modality) {
    const card = document.getElementById(scenario);
    if (!card) return;

    card.querySelectorAll('.modality-content').forEach(c => c.classList.remove('active'));
    card.querySelectorAll('.modality-tab').forEach(t => t.classList.remove('active'));

    const content = document.getElementById(`${scenario}-${modality}`);
    if (content) {
        content.classList.add('active');
    }

    if (event && event.target) {
        event.target.classList.add('active');
    }
}

/**
 * Show a specific tense (present, past, future, advanced) within a modality
 */
function showTense(scenario, modality, tense) {
    // New architecture: tense-content divs are siblings in the same page
    // Try the old container-based approach first for backwards compatibility
    const container = document.getElementById(`${scenario}-${modality}`);

    if (container) {
        // Old architecture: content is inside a container
        container.querySelectorAll('.tense-content').forEach(c => c.classList.remove('active'));
        container.querySelectorAll('.tense-btn').forEach(b => b.classList.remove('active'));
    } else {
        // New architecture: content divs are siblings, search the whole document
        document.querySelectorAll('.tense-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.tense-btn').forEach(b => b.classList.remove('active'));
    }

    // Activate the selected tense content
    const content = document.getElementById(`${scenario}-${modality}-${tense}`);
    if (content) {
        content.classList.add('active');
    }

    // Activate the clicked button
    if (typeof event !== 'undefined' && event && event.target) {
        event.target.classList.add('active');
    }
}

/**
 * Alias for showTense to support legacy button calls
 * Handles both old format: switchTense('shopping-story', 'present', this)
 * And new format: switchTense('shopping', 'story', 'present')
 */
function switchTense(scenarioOrComposite, modalityOrTense, tenseOrButton) {
    // Handle old format: switchTense('shopping-story', 'present', button)
    if (typeof tenseOrButton === 'object' || arguments.length === 3) {
        const parts = scenarioOrComposite.split('-');
        const scenario = parts[0];
        const modality = parts[1];
        const tense = modalityOrTense;
        showTense(scenario, modality, tense);
    }
    // Handle new format: switchTense('shopping', 'story', 'present')
    else {
        showTense(scenarioOrComposite, modalityOrTense, tenseOrButton);
    }
}

// ============================================================================
// AUDIO FUNCTIONS
// ============================================================================

/**
 * Speak Japanese text using Web Speech API
 */
function speak(text, button) {
    // Cancel any ongoing speech
    speechSynthesis.cancel();

    // Visual feedback
    if (button) {
        button.style.transform = 'scale(1.2)';
        setTimeout(() => button.style.transform = 'scale(1)', 200);
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ja-JP';
    utterance.rate = 0.8; // Slightly slower for learning
    speechSynthesis.speak(utterance);
}

// ============================================================================
// INTERACTIVE ELEMENTS
// ============================================================================

/**
 * Toggle hint visibility for dialogue lines, paragraphs, or phrases
 */
function toggleHint(btn) {
    // Try multiple patterns to find the hint element
    const hint = btn.parentElement.querySelector('.hint-text') ||
                btn.parentElement.querySelector('.paragraph-hint') ||
                btn.parentElement.querySelector('.phrase-hint') ||
                btn.closest('.speech-bubble')?.querySelector('.hint-text') ||
                btn.closest('.tip-box')?.querySelector('.hint-text') ||
                btn.nextElementSibling;

    if (hint) {
        hint.classList.toggle('show');
        btn.textContent = hint.classList.contains('show') ? 'Hide' : '?';
    }
}

/**
 * Toggle kanji card details (readings and meanings)
 * Also plays audio of the kanji when expanded
 */
function toggleKanji(card) {
    const details = card.querySelector('.kanji-details');
    if (details) {
        const wasShown = details.classList.contains('show');
        details.classList.toggle('show');

        // Play audio when expanding (not when collapsing)
        if (!wasShown) {
            const kanjiChar = card.querySelector('.kanji-character');
            if (kanjiChar) {
                speak(kanjiChar.textContent.trim());
            }
        }
    }
}

// ============================================================================
// QUIZ FUNCTIONS
// ============================================================================

/**
 * Check quiz answer and provide feedback
 */
function checkQuiz(el, correct, quizId) {
    if (answeredQuizzes.has(quizId)) return;
    answeredQuizzes.add(quizId);
    totalAnswered++;

    const options = el.parentElement.querySelectorAll('.option');
    options.forEach(opt => {
        opt.classList.add('disabled');
        if (opt === el) {
            opt.classList.add(correct ? 'correct' : 'incorrect');
        } else if (opt.onclick?.toString().includes('true')) {
            opt.classList.add('correct');
        }
    });

    const feedback = document.getElementById('feedback-' + quizId);
    if (correct) {
        score++;
        feedback.className = 'feedback show correct';
        feedback.textContent = '✓ 正解！ (Correct!)';
    } else {
        feedback.className = 'feedback show incorrect';
        feedback.textContent = '✗ 残念！正解は緑色です。 (The correct answer is in green.)';
    }

    updateScore();
}

/**
 * Update the score display
 */
function updateScore() {
    const scoreEl = document.getElementById('score');
    if (scoreEl) {
        scoreEl.textContent = `Score: ${score}/${totalAnswered}`;
        const percentage = totalAnswered > 0 ? (score / totalAnswered * 100).toFixed(0) : 0;

        if (percentage >= 80) {
            scoreEl.className = 'score-display excellent';
        } else if (percentage >= 60) {
            scoreEl.className = 'score-display good';
        } else {
            scoreEl.className = 'score-display';
        }
    }
}

/**
 * Reset quiz progress
 */
function resetQuiz() {
    answeredQuizzes.clear();
    score = 0;
    totalAnswered = 0;
    updateScore();

    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('disabled', 'correct', 'incorrect');
    });

    document.querySelectorAll('.feedback').forEach(fb => {
        fb.classList.remove('show');
    });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Initialize page - called on page load
 */
function initializePage() {
    // Stop any speech when page loads
    speechSynthesis.cancel();

    // Initialize score display
    updateScore();

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key stops speech
        if (e.key === 'Escape') {
            speechSynthesis.cancel();
        }
    });
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}
