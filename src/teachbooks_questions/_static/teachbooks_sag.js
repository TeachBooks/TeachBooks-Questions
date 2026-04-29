// Functionality for short-answer gaps questions in Teachbooks

(function () {
    document.addEventListener('click', function (event) {
        const resetButton = event.target.closest('div.sd-card.reset-button');
        if (resetButton) {
            handleResetClick(resetButton);
            return;
        }

        const submitButton = event.target.closest('div.sd-card.submit-button');
        if (submitButton) {
            handleSubmitClick(submitButton);
            return;
        }

        const showButton = event.target.closest('div.sd-card.show-button');
        if (showButton) {
            handleShowClick(showButton);
        }
    });

  document.addEventListener('focus', function (event) {
    if (event.target.tagName === 'INPUT') {
      handleFocus(event.target);
    }
    if (event.target.tagName === 'MATH-FIELD') {
      handleFocus(event.target);
    }
  }, true);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configureAllMathFields, { once: true });
  } else {
    configureAllMathFields();
  }

  function getQuestionDiv(element) {
    return element.closest('div.short-answer.gaps');
  }

  function getQuestionText(questionDiv) {
    return document.querySelector(`section.question-text#${questionDiv.id}-question`);
  }

  function setReadOnlyState(inputField, mathField, readOnly) {
    if (inputField) {
      inputField.readOnly = readOnly;
    }
    if (mathField) {
      mathField.readOnly = readOnly;
      if (readOnly) {
        mathField.setAttribute('read-only', '');
      } else {
        mathField.removeAttribute('read-only');
      }
    }
  }

  function handleShowClick(showButton) {
    const questionDiv = getQuestionDiv(showButton);
    if (!questionDiv) {
      return;
    }

    const questionText = getQuestionText(questionDiv);
    if (!questionText) {
      return;
    }

    questionText.querySelectorAll('span.inline-card.field').forEach(function (fieldCard) {
      const footer = fieldCard.querySelector('span.inline-card-footer');
      const inputField = fieldCard.querySelector('input.question-option-input');
      const mathField = fieldCard.querySelector('math-field.question-option-input');
      const answerSpan = fieldCard.querySelector('span.inline-card-feedback.answer');

      if (!footer || (!inputField && !mathField)) {
        return;
      }

      footer.classList.remove('correct','incorrect', 'parsing-error');
      footer.classList.add('show-answer');

      if (inputField) {
        inputField.classList.add('show-answer');
      }
      if (mathField) {
        mathField.classList.add('show-answer');
      }
      setReadOnlyState(inputField, mathField, true);

      if (answerSpan) {
        if (inputField) {
          // show the first answer if there are multiple, as the input field is not designed to show multiple answers
          inputField.value = answerSpan.textContent.trim().split(/(?<!\\);/)[0];
        }
        if (mathField) {
          if (mathField.classList.contains('type-M')) {
            // for M type, we want to show just the first correct answer
            const correctAnswers = answerSpan.textContent.trim().split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
            mathField.value = correctAnswers[0] || '';
          } else if (mathField.classList.contains('type-MR') || mathField.classList.contains('type-MNR')) {
            // for M(N)R type, we want to show some extra text to indicate the correct answer is a range
            // Keep it short, because little space in math fields
            mathField.value = 'x\\in\\mathbb{R}:' + answerSpan.textContent.trim().replace(/>=/g, "\\geq").replace(/<=/g, "\\leq");
          } else if (mathField.classList.contains('type-MAP') || mathField.classList.contains('type-MRP')) {
            // for MAP/MRP type, we want to show just the answer, as precision is not relevant to show
            parts = answerSpan.textContent.trim().split(';');
            centre = parts[0].trim();
            mathField.value = centre;
          }
        }
      }
    });
  }
  
  function clearShowAnswerMode(questionDiv, clearValues, clearAllInputs) {
    if (!questionDiv) {
      return;
    }

    questionDiv.querySelectorAll('span.inline-card.field').forEach(function (optionCard) {
      const inputField = optionCard.querySelector('input.question-option-input');
      const mathField = optionCard.querySelector('math-field.question-option-input');

      if (inputField && inputField.classList.contains('show-answer')) {
        if (clearValues || clearAllInputs) {
          inputField.value = '';
        }
        inputField.classList.remove('show-answer');
      } else if (inputField && clearAllInputs) {
        inputField.value = '';
      }

      if (mathField && mathField.classList.contains('show-answer')) {
        if (clearValues || clearAllInputs) {
          mathField.value = '';
        }
        mathField.classList.remove('show-answer');
      } else if (mathField && clearAllInputs) {
        mathField.value = '';
      }

      setReadOnlyState(inputField, mathField, false);
    });
  }

  function handleResetClick(resetButton) {

    const questionDiv = getQuestionDiv(resetButton);
    if (!questionDiv) {
      return;
    }

    const questionText = getQuestionText(questionDiv);
    if (!questionText) {
      return;
    }

    if (questionText) {
      clearShowAnswerMode(questionDiv, true, true);
      questionText.querySelectorAll('span.inline-card-footer').forEach(function (footer) {
        footer.classList.remove('correct', 'incorrect', 'parsing-error','show-answer');
      });
    }
  }

  function handleSubmitClick(submitButton) {
    const questionDiv = getQuestionDiv(submitButton);
    if (!questionDiv) {
      return;
    }

    // Clear show-answer mode in this question before checking submitted answers
    clearShowAnswerMode(questionDiv, true, false);

    const questionText = getQuestionText(questionDiv);
    if (!questionText) {
      return;
    }

    questionText.querySelectorAll('span.inline-card.field').forEach(function (fieldCard) {
      const footer = fieldCard.querySelector('span.inline-card-footer');
      const inputField = fieldCard.querySelector('input.question-option-input');
      const mathField = fieldCard.querySelector('math-field.question-option-input');
      const answerSpan = fieldCard.querySelector('span.inline-card-feedback.answer');

      
      if (!footer || (!inputField && !mathField)) {
        return;
      }

      footer.classList.remove('correct', 'incorrect', 'parsing-error','show-answer');

      // Now check the submitted answer for parsing errors and correctness
      if (mathField) {
        parsed = ce.parse(mathField.value).evaluate().json;
        if (containsError(parsed)) {
          // display the footer as incorrect with a message about parsing error.
          // done by the class 'parsing-error'
          footer.classList.add('parsing-error');
          return;
        }
      }

      const answerType = getAnswerType(inputField || mathField);
      const correctAnswer = answerSpan ? answerSpan.textContent.trim() : null;
      const isCorrect = checkAnswer(inputField ? inputField.value : mathField.value, correctAnswer, answerType);

      footer.classList.add(isCorrect ? 'correct' : 'incorrect');
    });
  }

  function getAnswerType(inputOrMathField) {
    if (inputOrMathField.classList.contains('type-T')) return 'T';
    if (inputOrMathField.classList.contains('type-TI')) return 'TI';
    if (inputOrMathField.classList.contains('type-TF')) return 'TF';
    if (inputOrMathField.classList.contains('type-M')) return 'M';
    if (inputOrMathField.classList.contains('type-MR')) return 'MR';
    if (inputOrMathField.classList.contains('type-MNR')) return 'MNR';
    if (inputOrMathField.classList.contains('type-MAP')) return 'MAP';
    if (inputOrMathField.classList.contains('type-MRP')) return 'MRP';
    return null;
  }

  function checkAnswer(studentAnswer, correctAnswer, answerType) {
    const stripped = studentAnswer.trim();

    if (stripped === '') {
      return false;
    }

    if (!answerType || !correctAnswer) {
      return false;
    }

    switch (answerType) {
      case 'T':
        // split the correct answer at unescaped ';' to allow for multiple correct answers, and trim each resulting answer
        const correctAnswersT = correctAnswer.split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
        // check if the stripped student answer matches any of the correct answers exactly
         return correctAnswersT.includes(stripped)
      case 'TI':
        // split the correct answer at unescaped ';' to allow for multiple correct answers, and trim each resulting answer
        const correctAnswersTI = correctAnswer.split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';').toLowerCase());
        // check if the stripped student answer matches any of the correct answers case-insensitively
        return correctAnswersTI.includes(stripped.toLowerCase());
      case 'TF':
        // split the correct answer at unescaped ';' to allow for multiple correct answers, and trim each resulting answer
        const correctAnswersTF = correctAnswer.split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
        // check if the stripped student answer matches any of the correct answers case-insensitively
        for (let ans of correctAnswersTF) {
          if (tunedSimilarity(stripped, ans) >= 0.9) {
            return true; // If we've already found a correct answer, no need to check further
          }
        }
        return false; // If no correct answer matched, return false
      case 'M':
        // convert both to Expressions and compare
        try {
          // loop over correct answers split at unescaped ';' to allow for multiple correct answers, and return true if any of them matches the student answer
          const correctAnswersM = correctAnswer.split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
          let correctlyAnswered = false;
          for (let ans of correctAnswersM) {
            if (correctlyAnswered) {
              break; // If we've already found a correct answer, no need to check further
            }
            const studentExpr = ce.parse(stripped);
            const correctExpr = ce.parse(ans);
            const studentEquation = studentExpr.head === 'Equal';
            const correctEquation = correctExpr.head === 'Equal';
            if (studentEquation && correctEquation) {
              const evalStudentExpr = ce.box(["Subtract", studentExpr.ops[0], studentExpr.ops[1]]).simplify();
              const evalCorrectExpr = ce.box(["Subtract", correctExpr.ops[0], correctExpr.ops[1]]).simplify();
              if (evalStudentExpr.isEqual(evalCorrectExpr)) {
                correctlyAnswered = true;
              }
              negateStudent = ce.box(["Negate", evalStudentExpr]).simplify();
              if (negateStudent.isEqual(evalCorrectExpr)) {
                correctlyAnswered = true;
              }
            } else if (!studentEquation && !correctEquation) {
              if (studentExpr.isEqual(correctExpr)) {
                correctlyAnswered = true;
              }
            }
          }
          return correctlyAnswered;
        }
        catch (e) {
          console.error('Error parsing math input: ', e);
          return false;
        }
      case 'MR':
        try {
          return valueInInterval(stripped, correctAnswer);
        }
        catch (e) {
          console.error('Error parsing math input for range checking: ', e);
          return false;
        }
      case 'MNR':
        try {
          return valueInIntervalNumerical(stripped, correctAnswer);
        }
        catch (e) {
          console.error('Error parsing math input for numerical range checking: ', e);
          return false;
        }
      case 'MAP':
        try {
          const parts = correctAnswer.split(';');
          if (parts.length !== 2) {
            console.error('Invalid correct answer format for MAP type. Expected "centre;precision". Got: ', correctAnswer);
            return false;
          }
          return checkAbsolutePrecision(stripped, parts[0], parts[1]);
        }
        catch (e) {
          console.error('Error parsing math input for absolute precision checking: ', e);
          return false;
        }
      case 'MRP':
        try {
          const parts = correctAnswer.split(';');
          if (parts.length !== 2) {
            console.error('Invalid correct answer format for MRP type. Expected "centre;precision". Got: ', correctAnswer);
            return false;
          }
          return checkRelativePrecision(stripped, parts[0], parts[1]);
        }
        catch (e) {
          console.error('Error parsing math input for absolute precision checking: ', e);
          return false;
        }
      default:
        console.error('Answer checking for type '+answerType+' is not implemented yet');
        return false;
    }
  }

  function handleFocus(element) {
    // In show-answer mode, focusing should not reset content;
    // users should leave this mode via Try again (or Submit).
    if (element.classList && element.classList.contains('show-answer')) {
      return;
    }
    if (element.tagName === 'INPUT' && element.readOnly) {
      return;
    }
    if (element.tagName === 'MATH-FIELD' && (element.readOnly || element.hasAttribute('read-only'))) {
      return;
    }

    // get the parent question div
    const questionDiv = getQuestionDiv(element);
    if (!questionDiv) {
      return;
    }
    // Remove all shown answers when resuming input mode
    clearShowAnswerMode(questionDiv, true, false);
    // Remove all feedback
    questionDiv.querySelectorAll('span.inline-card-footer').forEach(function (footer) {
      footer.classList.remove('correct', 'incorrect', 'parsing-error','show-answer');
    });
  }

  const MATH_SCROLL_STYLE_ID = 'data-tb-visible-scrollbar';

  function configureMathFieldHorizontalScroll(mathField) {
    if (!mathField) {
      return;
    }

    const apply = () => {
      const shadow = mathField.shadowRoot;
      if (!shadow) {
        return false;
      }

      // Add internal styles once: MathLive renders in shadow DOM, so host CSS is not enough.
      let styleTag = shadow.querySelector(`style[${MATH_SCROLL_STYLE_ID}]`);
      if (!styleTag) {
        styleTag = document.createElement('style');
        styleTag.setAttribute(MATH_SCROLL_STYLE_ID, '1');
        styleTag.textContent = `
          .ML__container,
          [part="container"] {
            display: flex !important;
            align-items: center;
            overflow-x: hidden !important;
            overflow-y: hidden !important;
          }

          .ML__content,
          [part="content"] {
            flex: 1 1 auto;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            white-space: nowrap !important;
            width: auto !important;
            min-width: 0 !important;
            -webkit-overflow-scrolling: touch;
            scrollbar-gutter: stable;
          }

          .ML__toggles,
          .ML__virtual-keyboard-toggle,
          .ML__menu-toggle {
            flex: 0 0 auto !important;
          }

          .ML__toggles {
            display: flex !important;
            flex-direction: row !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: fit-content !important;
            max-width: fit-content !important;
            min-width: 0 !important;
            gap: 0.1rem !important;
            column-gap: 0.1rem !important;
            row-gap: 0 !important;
            white-space: nowrap;
            grid-template-columns: none !important;
            margin: 0 !important;
            margin-left: 0.5rem !important;
            padding: 0 !important;
          }

          .ML__toggles--vertical {
            display: flex !important;
            flex-direction: row !important;
            grid-template-columns: none !important;
            row-gap: 0 !important;
            column-gap: 0.5rem !important;
            width: fit-content !important;
            max-width: fit-content !important;
          }

          .ML__toggles > * {
            flex: 0 0 auto !important;
            margin: 0 !important;
            min-width: 0 !important;
          }

          .ML__virtual-keyboard-toggle,
          .ML__menu-toggle {
            display: inline-flex !important;
            align-items: center;
            justify-content: center;
            margin: 0 !important;
            margin-inline: 0 !important;
            margin-inline-start: 0 !important;
            margin-inline-end: 0 !important;
            padding-left: 0.1rem;
            padding-right: 0.1rem;
            min-width: 0 !important;
            width: auto !important;
          }

          /* Keep scrolling possible on touch even when unfocused */
          :host(:not(:focus)) .ML__container,
          :host(:not(:focus-within)) .ML__container {
            pointer-events: auto !important;
          }

          /* Scrollbar styling for the input area */
          .ML__content::-webkit-scrollbar,
          [part="content"]::-webkit-scrollbar {
            height: 12px;
          }
          .ML__content::-webkit-scrollbar-thumb,
          [part="content"]::-webkit-scrollbar-thumb {
            background: rgba(120, 120, 120, 0.75);
            border-radius: 8px;
          }
          .ML__content::-webkit-scrollbar-track,
          [part="content"]::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.08);
          }
        `;
        shadow.appendChild(styleTag);
      }

      const content = shadow.querySelector('.ML__content, [part="content"]');

      return Boolean(content);
    };

    if (!apply()) {
      requestAnimationFrame(() => {
        if (!apply()) {
          setTimeout(apply, 50);
        }
      });
    }
  }

  function configureAllMathFields() {
    document
      .querySelectorAll('math-field.question-option-input')
      .forEach((mathField) => configureMathFieldHorizontalScroll(mathField));
  }

})();