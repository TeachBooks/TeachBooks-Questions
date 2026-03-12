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
:show:

<pre-questipn>
---
<question>
---
<post-question>
:::
````

Each of the options and placeholders will be shortly explained next:

- `<title>`: Including a title is optional.
- `:label: <label>`: Adding a label is optional. Can be used for unnumbered internal references.
- `:type: <type>`: Defines the type of the question. Available are `multiple-choice` and `short-answer`. If not given, _defaults_ to `multiple-choice`.
- `:variant: <variant>`: Defines the variant within the type of the question. If not given, the default value for the type is selected. For the type `multiple-choice` the variants `single-select` (_default_) and `multiple-select` are available. For the type `short-answer` the variant `block` (_default_) is available.

## Documentation

Further documentation for this extension is available in the [TeachBooks manual](https://teachbooks.io/manual/_git/github.com_TeachBooks_Sphinx-Metadata-Figure/main/MANUAL.html).

<!-- Start contribute -->
## Contribute

This tool's repository is stored on [GitHub](https://github.com/TeachBooks/Sphinx-Metadata-Figure). If you'd like to contribute, you can create a fork and open a pull request on the [GitHub repository](https://github.com/TeachBooks/Sphinx-Metadata-Figure).
