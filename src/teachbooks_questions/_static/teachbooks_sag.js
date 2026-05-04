// Functionality for short-answer gaps questions in Teachbooks

import { ComputeEngine } from "https://esm.run/@cortex-js/compute-engine@0.55.6";
import {
  checkAbsolutePrecision,
  checkRelativePrecision,
  containsError,
  tunedSimilarity,
  valueInInterval,
  valueInIntervalNumerical,
} from "./teachbooks_math_utils.js";
const ce = new ComputeEngine();

(function () {
  function parseEvalfDigits(evalfSetting) {
    if (!evalfSetting) return null;

    const value = String(evalfSetting).trim().toLowerCase();
    if (value === '' || value === 'no' || value === 'false' || value === '0') {
      return null;
    }
    if (value === 'yes' || value === 'true') {
      return 5;
    }

    const digits = Number.parseInt(value, 10);
    if (Number.isInteger(digits) && digits > 0) {
      return digits;
    }

    return null;
  }

  function isPlainFloatString(value) {
    const trimmed = String(value).trim();
    return /^[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?$/.test(trimmed);
  }

  function formatEvalfDisplay(expression, evalfSetting, exactFirst = true) {
    const trimmed = String(expression || '').trim();
    if (!trimmed || isPlainFloatString(trimmed)) {
      return trimmed;
    }

    const digits = parseEvalfDigits(evalfSetting);
    if (digits === null) {
      return trimmed;
    }

    try {
      const numeric = ce.parse(trimmed).N().valueOf();
      if (typeof numeric !== 'number' || !Number.isFinite(numeric)) {
        return trimmed;
      }
      const approxValue = Number(numeric).toPrecision(digits);
      return exactFirst
        ? `${trimmed} \\approx ${approxValue}`
        : `${approxValue} \\approx ${trimmed}`;
    } catch (error) {
      return trimmed;
    }
  }

  function operatorToLatex(operator) {
    if (operator === '<=') return '\\leq';
    if (operator === '>=') return '\\geq';
    return operator;
  }

  function parseLeadingBound(part) {
    if (part.startsWith('<=')) return { operator: '<=', expression: part.slice(2) };
    if (part.startsWith('>=')) return { operator: '>=', expression: part.slice(2) };
    if (part.startsWith('<')) return { operator: '<', expression: part.slice(1) };
    if (part.startsWith('>')) return { operator: '>', expression: part.slice(1) };
    return null;
  }

  function parseTrailingBound(part) {
    if (part.endsWith('<=')) return { operator: '<=', expression: part.slice(0, -2) };
    if (part.endsWith('>=')) return { operator: '>=', expression: part.slice(0, -2) };
    if (part.endsWith('<')) return { operator: '<', expression: part.slice(0, -1) };
    if (part.endsWith('>')) return { operator: '>', expression: part.slice(0, -1) };
    return null;
  }

  function formatRangeEvalfDisplay(intervalExpression, evalfSetting) {
    const compact = String(intervalExpression || '').replace(/\s+/g, '');
    if (!compact) {
      return '';
    }

    const parts = compact.split('x');
    if (parts.length !== 2) {
      return compact.replace(/>=/g, '\\geq').replace(/<=/g, '\\leq');
    }

    if (parts[0] === '') {
      const right = parseLeadingBound(parts[1]);
      if (!right) {
        return compact.replace(/>=/g, '\\geq').replace(/<=/g, '\\leq');
      }
      return `x ${operatorToLatex(right.operator)} ${formatEvalfDisplay(right.expression, evalfSetting)}`;
    }

    if (parts[1] === '') {
      const left = parseTrailingBound(parts[0]);
      if (!left) {
        return compact.replace(/>=/g, '\\geq').replace(/<=/g, '\\leq');
      }
      return `${formatEvalfDisplay(left.expression, evalfSetting, false)} ${operatorToLatex(left.operator)} x`;
    }

    const left = parseTrailingBound(parts[0]);
    const right = parseLeadingBound(parts[1]);
    if (!left || !right) {
      return compact.replace(/>=/g, '\\geq').replace(/<=/g, '\\leq');
    }

    return `${formatEvalfDisplay(left.expression, evalfSetting, false)} ${operatorToLatex(left.operator)} x ${operatorToLatex(right.operator)} ${formatEvalfDisplay(right.expression, evalfSetting)}`;
  }
    
    document.addEventListener("change", (event) => {
    const select = event.target.closest("select");
    if (!select) return;

    updateSelectState(select);
    });


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
    if (event.target.tagName === 'SELECT') {
      handleFocus(event.target);
    }
  }, true);
  
  
    function updateSelectState(select) {
        const option = select.selectedOptions[0];

        if (!option) return;

        select.classList.toggle(
            "default-selected",
            option.classList.contains("default")
        );
    }



  function getQuestionDiv(element) {
    return element.closest('div.short-answer.gaps');
  }

  function getQuestionText(questionDiv) {
    return document.querySelector(`section.question-text#${questionDiv.id}-question`);
  }

  function setReadOnlyState(inputField, mathField, selectField, readOnly) {
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
    if (selectField) {
      selectField.disabled = readOnly;
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
      const selectField = fieldCard.querySelector('select.question-option-input');
      const answerSpan = fieldCard.querySelector('span.inline-card-feedback.answer');

      if (!footer || (!inputField && !mathField && !selectField)) {
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
      if (selectField) {
        selectField.classList.add('show-answer');
      }
      setReadOnlyState(inputField, mathField, selectField, true);

      if (answerSpan) {
        if (inputField) {
          // show the first answer if there are multiple, as the input field is not designed to show multiple answers
          inputField.value = answerSpan.textContent.trim().split(/(?<!\\);/)[0];
        }
        if (mathField) {
          const evalfSetting = mathField.dataset ? mathField.dataset.evalf : null;
          if (mathField.classList.contains('type-M')) {
            // for M type, we want to show just the first correct answer
            const correctAnswers = answerSpan.textContent.trim().split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
            mathField.value = formatEvalfDisplay(correctAnswers[0] || '', evalfSetting);
          } else if (mathField.classList.contains('type-MR') || mathField.classList.contains('type-MNR')) {
            // for M(N)R type, we want to show some extra text to indicate the correct answer is a range
            // Keep it short, because little space in math fields
            mathField.value = 'x\\in\\mathbb{R}:' + formatRangeEvalfDisplay(answerSpan.textContent.trim(), evalfSetting);
          } else if (mathField.classList.contains('type-MAP') || mathField.classList.contains('type-MRP')) {
            // for MAP/MRP type, we want to show just the answer, as precision is not relevant to show
            const parts = answerSpan.textContent.trim().split(';');
            const centre = parts[0].trim();
            mathField.value = formatEvalfDisplay(centre, evalfSetting);
          }
        }
        if (selectField) {
          // show the first answer if there are multiple, as the select field is not designed to show multiple answers
          const correctAnswer = answerSpan.textContent.trim().split(/(?<!\\);/)[0].trim();
          selectField.querySelectorAll('option').forEach(function (option) {
            if (option.textContent.trim() === correctAnswer) {
              option.selected = true;
            } else {
              option.selected = false;
            }
          });
          updateSelectState(selectField);
        }
      }
    });

    questionDiv.querySelectorAll('section.question-feedback div.sd-card').forEach(function (feedbackCard) {
      feedbackCard.classList.remove('show');
      if (feedbackCard.classList.contains('show-answer')) {
        feedbackCard.classList.add('show');
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
      const selectField = optionCard.querySelector('select.question-option-input');

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

      if (selectField && selectField.classList.contains('show-answer')) {
        if (clearValues || clearAllInputs) {
          selectField.querySelectorAll('option').forEach(function (option) {
            option.selected = false;
          });
          selectField.selectedIndex = 0;         
        }
        selectField.classList.remove('show-answer');
      }
        else if (selectField && clearAllInputs) {
          selectField.querySelectorAll('option').forEach(function (option) {
            option.selected = false;
          });
          selectField.selectedIndex = 0;
        }
      if (selectField) {
        updateSelectState(selectField);
      }
      
      setReadOnlyState(inputField, mathField, selectField, false);
    });

    questionDiv.querySelectorAll('section.question-feedback div.sd-card').forEach(function (feedbackCard) {
      feedbackCard.classList.remove('show');
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
      questionDiv.querySelectorAll('section.question-feedback div.sd-card').forEach(function (feedbackCard) {
        feedbackCard.classList.remove('show');
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

    let numberOfFields = 0;
    let numberOfCorrect = 0;
    questionText.querySelectorAll('span.inline-card.field').forEach(function (fieldCard) {
      numberOfFields++;
      const footer = fieldCard.querySelector('span.inline-card-footer');
      const inputField = fieldCard.querySelector('input.question-option-input');
      const mathField = fieldCard.querySelector('math-field.question-option-input');
      const selectField = fieldCard.querySelector('select.question-option-input');
      const answerSpan = fieldCard.querySelector('span.inline-card-feedback.answer');

      
      if (!footer || (!inputField && !mathField && !selectField)) {
        return;
      }

      footer.classList.remove('correct', 'incorrect', 'parsing-error','show-answer');

      // Now check the submitted answer for parsing errors and correctness
      if (mathField) {
        const parsed = ce.parse(mathField.value).evaluate().json;
        if (containsError(parsed)) {
          // display the footer as incorrect with a message about parsing error.
          // done by the class 'parsing-error'
          footer.classList.add('parsing-error');
          return;
        }
      }

      const answerType = getAnswerType(inputField || mathField || selectField);
      const correctAnswer = answerSpan ? answerSpan.textContent.trim() : null;
      let toCheck = '';
      if (inputField) {
        toCheck = inputField.value;
      } else if (mathField) {
        toCheck = mathField.value;
      } else if (selectField && answerType === 'DS') {
        toCheck = selectField.selectedOptions[0] ? selectField.selectedOptions[0].textContent : '';
      }
      const isCorrect = checkAnswer(toCheck, correctAnswer, answerType);

      footer.classList.add(isCorrect ? 'correct' : 'incorrect');
      if (isCorrect) {
        numberOfCorrect++;
      }
    });

    // Show feedback based on number of correct answers, remove all others
    let targetClass = '';
    if (numberOfCorrect === numberOfFields) {
      targetClass = 'correct';
    }
    else if (numberOfCorrect === 0) {
      targetClass = 'incorrect';
    }
    else {
      targetClass = 'mixed';
    }
    questionDiv.querySelectorAll('section.question-feedback div.sd-card').forEach(function (feedbackCard) {
      if (feedbackCard.classList.contains(targetClass)) {
        feedbackCard.classList.add('show');
      } else {
        feedbackCard.classList.remove('show');
      }
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
    if (inputOrMathField.classList.contains('type-DS')) return 'DS';
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
      case 'DS':
        // split the correct answer at unescaped ';' to allow for multiple correct answers, and trim each resulting answer
        const correctAnswersDS = correctAnswer.split(/(?<!\\);/).map(ans => ans.trim().replace(/\\;/g, ';'));
        // check if the stripped student answer matches any of the correct answers exactly
         return correctAnswersDS.includes(stripped)
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
              const negateStudent = ce.box(["Negate", evalStudentExpr]).simplify();
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
    if (element.tagName === 'SELECT' && element.disabled) {
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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', configureAllMathFields, { once: true });
  } else {
    configureAllMathFields();
  }

})();