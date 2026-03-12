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
[ ] This is third answer.
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
[ ] This is third answer.
> :::{warning}
That is not correct.
:::
[x] This is the correct answer.
---
Did you find all correct answers?
::::

To be written.

::::{include} README.md
:start-after: "<!-- Start contribute -->"
::::
