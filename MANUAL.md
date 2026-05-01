````{margin}

```{note}

{bdg-primary}`Sphinx Extension`
{bdg-link-light}`Included in TeachBooks Template <../../../external/template/README.html>`
{bdg-link-light}`Included in TeachBooks Favourites <../../../features/favourites.html>`

```

```{tip}
This section is useful for user type 3-5.
```

```{seealso}

[{octicon}`mark-github` Repository](https://github.com/TeachBooks/TeachBooks-Questions)

[{octicon}`book` Copyright and Licenses checklist](../../../workflows/collaboration.md)

```

````

::::{include} README.md
:start-after: "<!-- Start documentation -->"
:end-before: "## Documentation"
::::

## Examples

We start this section with show casing the three types of questions that can be created with this extension. Then we show how the effect of different options on the appearance of the questions.

### Multiple-choice single-select question

````text
::::{question} Multiple-choice Single-select
:type: multiple-choice
:variant: single-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
& Hint: This is a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
& Hint: This is another correct answer.
---
Did you find all correct answers?
::::
````

::::{question} Multiple-choice Single-select
:type: multiple-choice
:variant: single-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
& Hint: This is a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
& Hint: This is another correct answer.
---
Did you find all correct answers?
::::

### Multiple-choice multiple-select question

````text
::::{question} Multiple-choice Multiple-select
:type: multiple-choice
:variant: multiple-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
& Hint: This is a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
& Hint: This is another correct answer.
^^^
= You did a very good job! You found all the correct answers.
! Too bad, you missed a correct answer. 
---
Did you find all correct answers?
::::
````

::::{question} Multiple-choice Multiple-select
:type: multiple-choice
:variant: multiple-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
& Hint: This is a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
& Hint: This is another correct answer.
^^^
= You did a very good job! You found all the correct answers.
! Too bad, you missed a correct answer. 
---
Did you find all correct answers?
::::

### Short-answer blocks question

For this example we will only show case two input blocks, but more can be added if needed.

````text
::::{question} Short-answer blocks
:type: short-answer
:variant: blocks
:showanswer:

Fill in the correct answer in the input fields.
---
T[TeachBooks ; PRIME] The correct answer is _TeachBooks_ or **PRIME**:
= Perfect!
> Did you make a typo? Try again. Remember that the answer is case-sensitive.

MR[0<x<=1] The correct answer is a number between 0 and 1, but not including 0:
& Hint: The answer is a number, so it cannot be negative and cannot be larger than 1.
---
What do you think?
::::
````

::::{question} Short-answer blocks
:type: short-answer
:variant: blocks
:showanswer:

Fill in the correct answer in the input fields.
---
T[TeachBooks ; PRIME] The correct answer is _TeachBooks_ or **PRIME**:
= Perfect!
> Did you make a typo? Try again. Remember that the answer is case-sensitive.

MR[0<x<=1] The correct answer is a number between 0 and 1, but not including 0:
& Hint: The answer is a number, so it cannot be negative and cannot be larger than 1.
---
What do you think?
::::

### Short-answer blocks with approximation in shown answer

This example shows the E-mode syntax for math input. Checking behaves like the corresponding base mode, while the shown answer is displayed as a symbolic expression together with a numerical approximation.

````text
::::{question} Short-answer blocks with approximation
:type: short-answer
:variant: blocks
:showanswer:

Use show answer to see symbolic and approximate forms.
---
ME[\frac{153}{31};5] Enter a value equal to $\frac{153}{31}$:
= Correct.
> Try again.
& The shown answer uses $5$ significant digits.

MRE[0<x<\pi;6] Enter a value between $0$ and $\pi$:
& The shown answer for the center value is displayed with $6$ significant digits.
---
The shown answer will display forms like $\dfrac{153}{31} \approx 4.9355$.
::::
````

::::{question} Short-answer blocks with approximation
:type: short-answer
:variant: blocks
:showanswer:

Use show answer to see symbolic and approximate forms.
---
ME[\frac{153}{31};5] Enter a value equal to $\frac{153}{31}$:
= Correct.
> Try again.
& The shown answer uses $5$ significant digits.

MRE[0<x<\pi;6] Enter a value between $0$ and $\pi$:
& The shown answer for the center value is displayed with $6$ significant digits.
---
The shown answer will display forms like $\dfrac{153}{31} \approx 4.9355$.
::::

### Short-answer fill-in-the-gaps question

````text
::::{question} Short-answer fill-in-the-gaps question
:type: short-answer
:variant: gaps
:showanswer:

FIll in the gaps with the correct words and math.
---
DS[TUDOP ; {TeachBooks} ; COMBINE ;{PRIME} ;  Grasple]
= **Perfect!**
> _Really?_
This line should not be shown ever.
MR[0<x<=1]
& Hint: $0.5$ works.
TI[PRIME ; TeachBooks]
^^^
? This extension has been written by {gap}.

The number {gap} is between $0$ and $1$, but not $0$.

:::{tip}
A {gap} example that directives are allowed also.
:::

& Some hint when the show button is clicked.

This line should also be shown in that case.

! A mixed feelings feedback.
---
Hint: the first answer is either *TeachBooks* or **PRIME** and one of those two is also the third.
::::
````

::::{question} Short-answer fill-in-the-gaps question
:type: short-answer
:variant: gaps
:showanswer:

FIll in the gaps with the correct words and math.
---
DS[TUDOP ; {TeachBooks} ; COMBINE ;{PRIME} ;  Grasple]
= **Perfect!**
> _Really?_
This line should not be shown ever.
MR[0<x<=1]
& Hint: $0.5$ works.
TI[PRIME ; TeachBooks]
^^^
? This extension has been written by {gap}.

The number {gap} is between $0$ and $1$, but not $0$.

:::{tip}
A {gap} example that directives are allowed also.
:::

& Some hint when the show button is clicked.

This line should also be shown in that case.

! A mixed feelings feedback.
---
Hint: the first answer is either *TeachBooks* or **PRIME** and one of those two is also the third.
::::


### No-input no-submit question

````text
::::{question} No-input No-submit
:type: no-input
:variant: no-submit
This is a question without input fields or submit buttons. It can be used to provide information or ask reflective questions without the need for user input.
---
> This is the feedback that will be shown when the "Show answer" button is clicked. It can contain any content that Sphinx can render, including roles, directives and math. Code spanning multiple lines is also allowed.

= This is a second feedback option, which will be shown as a second card when the "Show answer" button is clicked.

! A third option is also available, which can be used for neutral or informative feedback that is neither correct nor incorrect.
---
::::
````

::::{question} No-input No-submit
:type: no-input
:variant: no-submit
This is a question without input fields or submit buttons. It can be used to provide information or ask reflective questions without the need for user input.
---
> This is the feedback that will be shown when the "Show answer" button is clicked. It can contain any content that Sphinx can render, including roles, directives and math. Code spanning multiple lines is also allowed.

= This is a second feedback option, which will be shown as a second card when the "Show answer" button is clicked.

! A third option is also available, which can be used for neutral or informative feedback that is neither correct nor incorrect.
---
::::

### Caption and title

*With caption, with title:*

````text
::::{question} Title

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} Title

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

*Without caption, with title:*

````text
::::{question} Title
:nocaption:

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} Title
:nocaption:

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::


*Without caption, without title:*

````text
::::{question}
:nocaption:

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question}
:nocaption:

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

*With caption, without title:*

````text
::::{question}

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} 

---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

### Columns

*Single column specified*

Resize the window to see the effect of the columns.

In this case always 3 columns will be shown.

````text
::::{question} Title
:columns: 3
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is another answer.
[x] This is yet another answer.
---
::::
````

::::{question} Title
:columns: 3
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is another answer.
[x] This is yet another answer.
---
::::

*Fours columns specified*

Resize the window to see the effect of the columns.

In this case 4 columns will be shown for the largest screens, but for smaller screens the number of columns will be reduced to fit the screen, first going to 3 columns, then 2 and finally 1.

````text
::::{question} Title
:columns: 1 2 3 4
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is another answer.
[x] This is yet another answer.
---
::::
````

::::{question} Title
:columns: 1 2 3 4
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is another answer.
[x] This is yet another answer.
---
::::

### Class and admonition

The custom CSS is included in this extension, so can be used if preferred.

*With admonition, without custom class*

````text
::::{question} Title
:admonition:
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} Title
:admonition:
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

*With admonition, with custom class*

````text
::::{question} Title
:admonition:
:class: teachbooks-question
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} Title
:admonition:
:class: teachbooks-question
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

*Without admonition, with custom class*

````text
::::{question} Title
:class: teachbooks-question
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::
````

::::{question} Title
:class: teachbooks-question
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
---
::::

### Show answer button

*Multiple-choice single-select question*

````text
::::{question} Multiple-choice Single-select
:type: multiple-choice
:variant: single-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
---
Did you find all correct answers?
::::
````

::::{question} Multiple-choice Single-select
:type: multiple-choice
:variant: single-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
---
Did you find all correct answers?
::::

*Multiple-choice multiple-select question*

````text
::::{question} Multiple-choice Multiple-select
:type: multiple-choice
:variant: multiple-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
---
Did you find all correct answers?
::::
````

::::{question} Multiple-choice Multiple-select
:type: multiple-choice
:variant: multiple-select
:showanswer:

Select a correct answer.
---
[x] This is an answer.
> Which is also a correct answer.
[ ] This is an incorrect answer.
[ ] This is the third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
---
Did you find all correct answers?
::::

*Short-answer blocks question*

````text
::::{question} Short-answer blocks
:type: short-answer
:variant: blocks
:showanswer:

Fill in the correct answer in the input fields.
---
T[TeachBooks] The correct answer is _TeachBooks_:
= Perfect!
> Did you make a typo? Try again. Remember that the answer is case-sensitive.

MR[0<x<=1] The correct answer is a number between 0 and 1, but not including 0:
---
What do you think?
::::
````

::::{question} Short-answer blocks
:type: short-answer
:variant: blocks
:showanswer:

Fill in the correct answer in the input fields.
---
T[TeachBooks] The correct answer is _TeachBooks_:
= Perfect!
> Did you make a typo? Try again. Remember that the answer is case-sensitive.

MR[0<x<=1] The correct answer is a number between 0 and 1, but not including 0:
---
What do you think?
::::

::::{include} README.md
:start-after: "<!-- Start contribute -->"
::::
