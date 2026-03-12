<!-- Start documentation -->
# TeachBooks Questions

A Sphinx extension to create and include multiple-choice and short-answer questions.

This extensions defines a `question` directive that typesets either a multiple-choice question or a short-answer question, including (automatic) feedback, buttons and styling options.

## Installation
To install the Sphinx-Metadata-Figure extension, follow these steps:

**Step 1: Install the Package**

Install the `TeachBooks Questions` package using `pip`:
```
pip install teachbooks-questions
```

**Step 2: Add to `requirements.txt`**

Make sure that the package is included in your project's `requirements.txt` to track the dependency:
```
teachbooks-questions
```

**Step 3: Enable in `_config.yml`**

In your `_config.yml` file, add the extension to the list of Sphinx extra extensions:
```
sphinx: 
    extra_extensions:
        - teachbooks_questions
```

## Configuration

In the current version no Sphinx configuration options are exposed currently.

## Usage

The directive `question` has the following full MarkDown syntax for use, where `<...>` are placeholders:

````text
:::{question} <title>
:label: <label>
:type: <type>
:variant: <variant>
:columns: <columns>
:class: <class>
:admonition:
:nocaption:
:showanswer:

<pre-question>
---
<question>
---
<post-question>
:::
````

### Rendering

The result of the `question` directive will be a `<div>` element containing, in order, the following elements (if provided/indicated):
- An optional title with(out) a caption or just a caption.
- Some content before the options/input fields.
- The options/input fields.
- Some content after the options/input fields.
- Buttons for interaction.

### Directive options and placeholders

Each of the options and placeholders will be shortly explained next:

- `<title>`: Including a title is optional.
- `:label: <label>`: Adding a label is optional. Can be used for unnumbered internal references.
- `:type: <type>`: Defines the type of the question. Available are `multiple-choice` and `short-answer`. If not given, _defaults_ to `multiple-choice`.
- `:variant: <variant>`: Defines the variant within the type of the question. If not given, the default value for the type is selected. For the type `multiple-choice` the variants `single-select` (_default_) and `multiple-select` are available. For the type `short-answer` the variant `block` (_default_) is available.
- `:columns: <columns>`: Number of columns to use for displaying the options for `multiple-choice` questions (_default_: `1 1 2 2`) or for the input blocks for the `short-answer block` questions (_default_: `1 1 1 1`). See [Grids](https://sphinx-design.readthedocs.io/en/latest/grids.html), second paragraph for more details. Either one single number or 4 numbers can be provided. If one single number is provided, it will be used for all screen sizes. If 4 numbers are provided, they will be used for the 4 screen sizes (small, medium, large and extra large) in that order.
- `:class: <class>`: The classes to be added to the class list of the `div` element for styling purposes.
- `:admonition:` If included, `admonition` will be added to the classes of the containing `<div>`. Can also be done through the `:class:` option.
- `:nocaption:` If included, no caption will be added to the question. By default, a caption is added with the text "Question". This option can be used to hide the caption. If also no title is provided, the question will have neither a title nor a caption shown. If a title is provided, the title will be shown without surrounding brackets.
- `:showanswer:`: If included, a button will be added to show the correct answer(s) and related feedback.
- `<pre-question>`: Optional content to be included before the options/input fields. Will be parsed, so nesting of elements is possible.
- `<question>`: Code that defines the content of the options/input fields, including (in)correct answers and feedback. See [Syntax for multiple-choice questions](#syntax-for-multiple-choice-questions) and [Syntax for short-answer blocks questions](#syntax-for-short-answer-blocks-questions). Everything between the first `---` and the second `---` is considered part of this part of the code.
- `<post-question>`: Optional content to be included after the options/input fields. Will be parsed, so nesting of elements is possible.

### Syntax for multiple-choice questions

The code inside `<question>` for `multiple-choice` questions is for both variants based on the same syntax.

To define a single correct option, add code of the form

````text
[x] <Option>
> <Feedback>
````

and to define a single incorrect option, add code of the form

````text
[ ] <Option>
> <Feedback>
````

The placeholder `<Option>` can be any code that can be parsed by Sphinx. This includes roles, directives and math. Code spanning multiple lines is also allowed, as long as the first line of the option starts with `[x] ` or `[ ] ` and is directly followed by some code. All following lines not starting with `[x] ` or `[ ] ` or `> ` are considered part of the same option.

The placeholder `<Feedback>` can be any code that can be parsed by Sphinx. This includes roles, directives and math. Code spanning multiple lines is also allowed, as long as the first line of the feedback starts with `> ` and is directly followed by some code. All following lines not starting with `[x] ` or `[ ] ` or `> ` are considered part of the same feedback. Feedback is optional, and if not provided, the feedback will be `Correct!` or `Incorrect.`, based on whether the previous option is correct (`[x] `) or incorrect (`[  ] `).

A short example of allowed code:

````text
[x] An option that

has several lines and is also marked as correct answer.

> :::{note}
You can include directives.
:::

[ ] An incorrect option.

> $$
\int_{a}^{b} f(x)\,dx.
$$

Display math is also possible.
````

### Syntax for short-answer blocks questions

The code inside `<question>` for `short-answer` questions for the variant `blocks` has the following syntax.

To add an input field, add code of the form

````text
<Mode>[<Answer>] <Label>
= <CorrectFeedback>
> <IncorrectFeedback>
````

The placeholder `<Mode>` must be one of the following modes: `T`, `TI`, `TF`, `M`, `MR`, `MNR`, `MAP`, `MRP`. The `<Mode>` defines the input method (text or math), how correctness of an answer is determined and what the placeholder `<Answer>` can be:

- `T[Answer]` for a short answer question with a text input field, which will be checked for an exact match with the provided answer.
- `TI[Answer]` for a short answer question with a text input field, which will be checked for a case-insensitive match with the provided answer.
- `TF[Answer]` for a short answer question with a text input field, which will be checked for a fuzzy case-insensitive match with the provided answer. Be aware that this can lead to some unexpected answers being marked as (in)correct, and it is recommended to use this option only for longer answers where minor typos are more likely to occur, and to check the provided answer carefully for potential issues with the fuzzy matching.
- `M[Answer]` for a short answer question with a math input field, which will check for a (simple) equality check with the provided answer using the function [`is()`](https://mathlive.io/compute-engine/guides/symbolic-computing/#smart-comparison-is) from the [MathLive Compute Engine](https://mathlive.io/compute-engine/).
- `MR[Answer] ` for a short answer question with a math input field, which will check whether the provided answer falls within the range defined by `Answer`. In this case `Answer` should be given as one of the following, where `a` and/or `b` should be replaced with the desired numbers, which can also include $\LaTeX$ math expressions that will be evaluated using the [MathLive Compute Engine](https://mathlive.io/compute-engine/). The value provided by the user will also be evaluated using the MathLive Compute Engine, and it will be checked whether this value falls within the defined range. Note that some expression will not evaluate to a number, unless explicitly numerically evaluated, and these will not be accepted as correct answers for `MR` type questions (see the `MNR` type for this). Examples of valid formats for `Answer` for `MR` type questions are:
  - `x < a` for values less than `a`.
  - `x <= a` for values less than or equal to `a`.
  - `x > a` for values greater than `a`.
  - `x >= a` for values greater than or equal to `a`.
  - `a < x < b` for values between `a` and `b`,
  - `a <= x < b` for values between `a` and `b`, including `a` but not `b`.
  - `a < x <= b` for values between `a` and `b`, including `b` but not `a`.
  - `a <= x <= b` for values between `a` and `b`, including both `a` and `b`.
- `MNR[Answer]` is similar to `MR[Answer]`, but the evaluation of the provided answer and the values in `Answer` will be explicitly numerically. This may cause unexpected results due to rounding errors.
- `MAP[Answer]` for a short answer question with a math input field, which will check for numerical equivalence between the provided answer and the correct answer up to a given absolute precision. In this case, `Answer` should be given in the format `CorrectAnswer;Precision`, where `CorrectAnswer` is the correct answer, which can include $\LaTeX$ math expressions that will be evaluated numerically using the [MathLive Compute Engine](https://mathlive.io/compute-engine/), and `Precision` is the desired absolute precision for the comparison, which should be a number (which can also include $\LaTeX$ math expressions that will be numerically evaluated using the MathLive Compute Engine). The provided answer will also be evaluated numerically using the MathLive Compute Engine, and it will be checked whether the absolute difference between the provided answer and the correct answer is less than or equal to the defined precision.
- `MRP[Answer]` is similar to `MAP[Answer]`, but it will check for numerical equivalence between the provided answer and the correct answer up to a given relative precision. In this case, `Answer` should be given in the format `CorrectAnswer;Precision`, where `CorrectAnswer` is the correct answer, which can include $\LaTeX$ math expressions that will be evaluated numerically using the [MathLive Compute Engine](https://mathlive.io/compute-engine/), and `Precision` is the desired relative precision for the comparison, which should be a number (which can also include $\LaTeX$ math expressions that will be numerically evaluated using the MathLive Compute Engine). The provided answer will also be evaluated numerically using the MathLive Compute Engine, and it will be checked whether the absolute value of the difference between the provided answer and the correct answer divided by the absolute value of the correct answer is less than or equal to the defined precision.

The placeholder `<Label>` is optional and if provided will be place above the input field. This can be any code that Sphinx can render. This includes roles, directives and math. Code spanning multiple lines is also allowed, as long as the first line of the option starts with `<Mode>[Answer] ` and is directly followed by some code. All following lines not starting with `<Mode>[Answer] ` or `= ` or `> ` are considered part of the same label.

A line starting with `= ` is considered the start of the feedback if a correct answer is entered. `<CorrectFeedback>` can be any code that Sphinx can render. This includes roles, directives and math. Code spanning multiple lines is also allowed, as long as the first line of the option starts with `= ` and is directly followed by some code. All following lines not starting with `<Mode>[Answer] ` or `= ` or `> ` are considered part of the same feedback. If not provided, the default `Correct!` will be substituted.

A line starting with `> ` is considered the start of the feedback if an incorrect answer is entered. `<IncorrectFeedback>` can be any code that Sphinx can render. This includes roles, directives and math. Code spanning multiple lines is also allowed, as long as the first line of the option starts with `> ` and is directly followed by some code. All following lines not starting with `<Mode>[Answer] ` or `= ` or `> ` are considered part of the same feedback. If not provided, the default `Incorrect.` will be substituted.

If between two lines starting with `<Mode>[Answer] ` multiple instances of correct feedback (`= `) are found, these will be concatenated. If between two lines starting with `<Mode>[Answer] ` multiple instances of incorrect feedback (`> `) are found, these will be concatenated.

## Documentation

Examples for this extension are available in the [TeachBooks manual](https://teachbooks.io/manual/_git/github.com_TeachBooks_TeachBooks-Questions/main/MANUAL.html).

<!-- Start contribute -->
## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/TeachBooks-Questions). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/TeachBooks-Questions).

## Stuff we would like to add in the future

- Add a variant `fill-in-the-gaps` to the type `short-answer`
- Add a dropdown mode for short-answer
- Add a javascript mode for short-answer
- Configuration options
- i18n
- ...
