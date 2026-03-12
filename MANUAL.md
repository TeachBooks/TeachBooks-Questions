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

### Multiple-choice multiple-select question

````text
::::{question} Multiple-choice Multiple-select
:type: multiple-choice
:variant: multiple-select

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

### Short-answer blocks question

For this example we will only show case two input blocks, but more can be added if needed.

````text
::::{question} Short-answer blocks
:type: short-answer
:variant: blocks
Fill in the correct answer in the input fields.
---
T[TeachBooks] The correct answer is _TeachBooks_:
= Perfect!
> Did you make a typo? Try again. Remember that the answer is case-sensitive.

MR[0<x<=1] The correct answer is a number between 0 and 1, but not including 0:
---
What do you think?
````


::::{include} README.md
:start-after: "<!-- Start contribute -->"
::::
