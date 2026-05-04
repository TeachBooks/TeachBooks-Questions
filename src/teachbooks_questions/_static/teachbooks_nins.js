// Functionality for no-input no-submit questions in Teachbooks

(function () {
    function handleResetClick(resetButton) {
        const questionDiv = getQuestionDiv(resetButton);
        if (!questionDiv) {
        return;
        }

        const questionOptionsSection = getQuestionOptionsSection(questionDiv);

        if (questionOptionsSection) {
        questionOptionsSection.querySelectorAll('div.sd-card').forEach(function (card) {
            card.classList.remove('correct', 'incorrect','neutral');
        });
        }
    }

    function handleShowClick(showButton) {
        const questionDiv = getQuestionDiv(showButton);
        if (!questionDiv) {
        return;
        }

        const questionOptionsSection = getQuestionOptionsSection(questionDiv);

        if (questionOptionsSection) {
        questionOptionsSection.querySelectorAll('div.sd-card').forEach(function (card) {
            cardSection = card.querySelector('section.question-option');
            if (cardSection) {
                if (cardSection.classList.contains('correct')) {
                    card.classList.add('correct');
                } else if (cardSection.classList.contains('incorrect')) {
                    card.classList.add('incorrect');
                } else if (cardSection.classList.contains('neutral')) {
                    card.classList.add('neutral');
                }
            }
        });
        }
    }

    function getQuestionOptionsSection(questionDiv) {
        return document.querySelector(`section.question-options#${questionDiv.id}-options`);
    }

    function getQuestionDiv(element) {
        return element.closest('div.no-input.no-submit');
    }

    document.addEventListener('click', function (event) {
        const resetButton = event.target.closest('div.sd-card.reset-button');
        if (resetButton) {
            handleResetClick(resetButton);
            return;
        }

        const showButton = event.target.closest('div.sd-card.show-button');
        if (showButton) {
            handleShowClick(showButton);
            return;
        }
    });
})();