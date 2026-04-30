document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("div.short-answer.gaps .question-surface span.inline-card-body math-field.question-option-input")
    .forEach(mathField => {
      // Fix the shadow DOM stuff
      const span = mathField.shadowRoot.querySelector('span');
      if (span) {
        span.style.display = 'block';
      }
    });
});
