import os
import re
from typing import List, Tuple, Dict, Any

from docutils import nodes
from sphinx.util.docutils import SphinxDirective
from docutils.nodes import Node
from docutils.parsers.rst import directives

# from sphinx.util import logging
# logger = logging.getLogger(__name__)


class QuestionDirective(SphinxDirective):
    # Configuration
    TYPES = ["multiple-choice", "short-answer","no-input"]
    VARIANTS = {
        "multiple-choice": ["single-select", "multiple-select"],
        "short-answer": ["blocks","gaps"],
        "no-input": ["no-submit"]
    }
    FEEDBACKS = {
        "multiple-choice": {
            "single-select": {True: ["Correct!"], False: ["Incorrect."]},
            "multiple-select": {True: ["Correct!"], False: ["Incorrect."],
                                "correct": ["Well done!"],
                                "incorrect" : ["Try again! You selected at least one incorrect option."],
                                "missed": ["Try again! You missed at least one correct option."],
                                "incorrect-missed": ["Try again! You selected at least one incorrect option and missed at least one correct option."] }
        },
        "short-answer": {
            "blocks": {True: ["Correct!"], False: ["Incorrect."]},
            "gaps": {True: ["Correct!"], False: ["Incorrect."],
                     "correct": ["You filled in all gaps correctly."],
                     "incorrect": ["You filled in none of the gaps correctly."],
                     "mixed": ["You filled in some gaps correctly, but also some incorrectly."],
                     "show-answer": ["The correct answers are shown above."] }
        },
        "no-input": {"no-submit": {}}

    }
    COLUMNS = {
        "multiple-choice": {"single-select": "1 1 2 2", "multiple-select": "1 1 2 2"},
        "short-answer": {"blocks": "1 1 1 1", "gaps": "1 1 1 1"},
        "no-input": {"no-submit": "1 1 1 1"}
    }
    
    # Patterns
    OPTION_CHECKBOX_UNCHECKED = "[ ] "
    OPTION_CHECKBOX_CHECKED = "[x] "
    FEEDBACK_WRONG_PREFIX = "> "
    FEEDBACK_CORRECT_PREFIX = "= "
    FEEDBACK_NEUTRAL_PREFIX = "! "
    FEEDBACK_SHOW_ANSWER_PREFIX = "& "
    QUESTION_STRUCTURE_PREFIX = "? "
    SEPARATOR = "---"
    GENERAL_FEEDBACK_SEPARATOR = "^^^"
    
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "class": directives.class_option,
        "label": directives.unchanged,
        "type": directives.unchanged,
        "variant": directives.unchanged,
        "columns": directives.unchanged,
        "admonition": directives.flag,
        "nocaption": directives.flag,
        "showanswer": directives.flag
    }

    def run(self) -> List[Node]:
        """Main directive handler."""
        # Validate and get question type and variant
        question_type = self.options.get("type", "multiple-choice")
        if question_type not in self.TYPES:
            raise ValueError(
                f"Unsupported question type {question_type} at line {self.lineno} in "
                f"{self.env.docname}. Supported types are: {self.TYPES}"
            )
        
        variant = self.options.get("variant", self.VARIANTS[question_type][0])
        if variant not in self.VARIANTS[question_type]:
            raise ValueError(
                f"Unsupported question variant {variant} for type {question_type} at line "
                f"{self.lineno} in {self.env.docname}. Supported variants are: "
                f"{self.VARIANTS[question_type]}"
            )
                
        columns = self.options.get("columns", self.COLUMNS[question_type][variant])
        feedback = self.options.get("feedback", self.FEEDBACKS[question_type][variant])

        # Get flags
        css_class = self.options.get("class", [])
        is_admonition = "admonition" in self.options
        no_caption = "nocaption" in self.options
        show_answer = "showanswer" in self.options
        if question_type == "no-input" and variant == "no-submit":
            show_answer = True  # Force show_answer for no-input no-submit questions

        # Create and configure node
        node = question_node()
        node["type"] = question_type
        node["variant"] = variant
        node["class"] = css_class
        node["admonition"] = is_admonition
        node["show_answer"] = show_answer
        
        # Create unique ID
        node_id = self._create_node_id()
        node["ids"] = [node_id]
        
        # Add title if provided
        if not self.arguments:
            self.arguments = [" "]
        if self.arguments:
            title_text = self._format_title(self.arguments[0], no_caption)
            textnodes, _ = self.state.inline_text(title_text, self.lineno)
            node_title = nodes.title(title_text, "", *textnodes, ids=[node_id + "-title"])
            node += node_title
        
        node["nocaption"] = no_caption

        # Dispatch to appropriate handler
        if question_type == "multiple-choice":
            if variant == "single-select":
                return self._handle_multiple_choice_single_select(node, node_id, columns, feedback)
            else:  # multiple-select
                return self._handle_multiple_choice_multiple_select(node, node_id, columns, feedback)
        elif question_type == "short-answer":
            if variant == "blocks":
                return self._handle_short_answer_blocks(node, node_id, feedback, columns)
            else:  # gaps
                return self._handle_short_answer_gaps(node, node_id, feedback, columns)
        else:  # no-input no-submit
            return self._handle_no_input_no_submit(node, node_id, feedback, columns)

    def _create_node_id(self) -> str:
        """Create a unique ID for the node."""
        if self.options.get("label"):
            return self.options["label"]
        return f"question-{self.env.new_serialno('question')}"

    def _format_title(self, title: str, no_caption: bool) -> str:
        """Format the title based on caption setting."""
        if no_caption:
            return title
        if title.strip() == "":
            return ""
        return f" ({title})"
            
    def _calculate_button_distribution(self, button_count: int) -> str:
        """Calculate grid distribution for buttons.
        
        Distributes buttons evenly across 4 grid positions.
        """
        if button_count == 0:
            return "1 1 1 1"
        
        positions = [1]
        if button_count > 1:
            positions.append(round(1 + (button_count - 1) / 3))
            positions.append(round(1 + 2 * (button_count - 1) / 3))
            positions.append(button_count)
        else:
            positions.extend([1, 1, 1])
        
        return " ".join(str(p) for p in positions)

    def _create_button_grid(
        self, button_dist: str, buttons: List[Tuple[str, str]]
    ) -> List[str]:
        """Create grid markup for buttons.
        
        Args:
            button_dist: Grid distribution string
            buttons: List of (css_class, label) tuples
            
        Returns:
            List of grid markup lines
        """
        grid = [f"::::{{grid}} {button_dist}", ":gutter: 3", ""]
        for css_class, label in buttons:
            grid.extend([
                ":::{grid-item-card}",
                ":shadow: lg",
                ":text-align: center",
                f":class-card: {css_class}",
                "",
                label,
                ":::",
            ])
        grid.append("::::")
        return grid

    def _add_text_section(
        self, node: Node, node_id: str, text: List[str], section_type: str
    ) -> None:
        """Add a text section to the node."""
        if text:
            section = nodes.section(
                classes=[f"question-{section_type}"],
                ids=[f"{node_id}-{section_type}"]
            )
            self.state.nested_parse(text, self.content_offset, section)
            node += section

    def _add_button_section(
        self,
        node: Node,
        node_id: str,
        buttons: List[Tuple[str, str]],
        show_answer: bool,
        button_count: int,
    ) -> None:
        """Add button section to node."""
        button_section = nodes.section(
            classes=["question-buttons"],
            ids=[f"{node_id}-buttons"]
        )
        button_dist = self._calculate_button_distribution(button_count)
        grid = self._create_button_grid(button_dist, buttons)
        self.state.nested_parse(grid, self.content_offset, button_section)
        node += button_section

    def _split_input(self) -> Tuple[List[str], List[str], List[str]]:
        """Split directive content into pre-text, options, and post-text."""
        separators = [i for i, line in enumerate(self.content) if line.strip() == self.SEPARATOR]
        
        if len(separators) < 2:
            raise ValueError(
                f"Malformed question at line {self.lineno} in {self.env.docname}. "
                f"Please provide options between '{self.SEPARATOR}' and '{self.SEPARATOR}'. "
                f"Found {len(separators)} separator(s), expected 2."
            )
        if len(separators) > 2:
            extra_lines = ", ".join(str(self.lineno + i) for i in separators[2:])
            raise ValueError(
                f"Too many separators in question at line {self.lineno} in {self.env.docname}. "
                f"Extra separators at lines: {extra_lines}"
            )
        # handle general feedback for multiple-select questions
        general_separator = [i for i, line in enumerate(self.content) if line.strip() == self.GENERAL_FEEDBACK_SEPARATOR]
        if len(general_separator) > 1:
            raise ValueError(
            f"Malformed question at line {self.lineno} in {self.env.docname}. "
            f"Please only provided one general feedback section"
            f"starting with '{self.GENERAL_FEEDBACK_SEPARATOR}'"
            f"between '{self.SEPARATOR}' and '{self.SEPARATOR}'. "
            f"Found {len(general_separator)} separator(s), expected at most 1."
        )

        if general_separator:
            pre_text = self.content[:separators[0]]
            options_raw = self.content[separators[0] + 1:general_separator[0]]
            general_raw = self.content[general_separator[0] + 1:separators[1]]
            post_text = self.content[separators[1] + 1:]
        else:
            pre_text = self.content[:separators[0]]
            options_raw = self.content[separators[0] + 1:separators[1]]
            post_text = self.content[separators[1] + 1:]
            general_raw = []

        return pre_text, options_raw, general_raw, post_text
    
    def _handle_no_input_no_submit(self, node: Node, node_id: str, feedback: Dict, columns: str) -> List[Node]:
        """Handle no-input no-submit questions."""
        pre_text, options_raw, _, post_text = self._split_input()

        # Add pre-text if present
        self._add_text_section(node, node_id, pre_text, "pretext")

        # Parse feedback options
        options_data = self._parse_no_input_options(options_raw, feedback, node_id)
        
        # Render feedback options as cards
        self._render_no_input_cards(node, node_id, options_data, columns)

        # Add post-text if present
        self._add_text_section(node, node_id, post_text, "posttext")

        # Add buttons
        button_count = 2 # Show answer and reset, no submit button
        buttons = []
        buttons.append(("show-button", "<i class='fa-solid fa-file-circle-check'></i> Show answer(s)"))
        buttons.append(("reset-button", "<i class='fa-solid fa-repeat'></i> Try again"))

        self._add_button_section(node, node_id, buttons, node["show_answer"], button_count)

        return [node]

    def _render_no_input_cards(self, node: Node, node_id: str, options: List[Dict], columns: str) -> None:
        """Render no-input feedback options as cards."""
        if not options:
            return
        
        # Create card grid markup
        cards_markup = [
            f"::::{{grid}} {columns}",
            ":gutter: 3",
            "",
        ]
        for _ in options:
            cards_markup.extend([
                ":::{grid-item-card}",
                ":shadow: lg",
                ":class-card: option",
                "",
                ":::",
            ])
        cards_markup.append("::::")

        # Render cards
        options_section = nodes.section(
            classes=["question-options"],
            ids=[f"{node_id}-options"]
        )
        self.state.nested_parse(cards_markup, self.content_offset, options_section)
        node += options_section

        # Populate card content
        current_card = -1
        for container in options_section.findall(nodes.container):
            card_classes = container.get("classes", [])
            
            if "sd-card-body" in card_classes:
                current_card += 1
                option = options[current_card]
                type_class = option["type"]
                option_section = nodes.section(
                    classes=[f"question-option {type_class}"],
                    ids=[f"{node_id}-option-{current_card}"]
                )
                self.state.nested_parse(
                    option["feedback"], self.content_offset, option_section
                )
                container += option_section

    def _parse_no_input_options(self, options_raw: List[str], feedback: Dict, node_id: str
    ) -> List[Dict[str, Any]]:
        """Parse feedback options for no-input questions."""
        if not options_raw:
            return []

        # Find option markers (lines starting with >, =, or ! for feedback)
        option_starts = [
            i for i, line in enumerate(options_raw)
            if line.rstrip().startswith(self.FEEDBACK_WRONG_PREFIX.rstrip())
            or line.rstrip().startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip())
            or line.rstrip().startswith(self.FEEDBACK_NEUTRAL_PREFIX.rstrip())
        ]

        options = []
        for idx, start in enumerate(option_starts):
            end = option_starts[idx + 1] if idx + 1 < len(option_starts) else len(options_raw)
            block = options_raw[start:end]
            option = self._parse_single_no_input_option(block, feedback)
            options.append(option)

        return options

    def _parse_single_no_input_option(self, block: List[str], feedback: Dict) -> Dict[str, Any]:
        """Parse a single feedback option for no-input questions."""
        first_line = block[0].rstrip()
        
        # Extract label (text after > or = or ! on first line and subsequent lines)
        if first_line.startswith(self.FEEDBACK_WRONG_PREFIX.rstrip()):
            label_start = first_line[len(self.FEEDBACK_WRONG_PREFIX.rstrip()):].strip()
        elif first_line.startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip()):
            label_start = first_line[len(self.FEEDBACK_CORRECT_PREFIX.rstrip()):].strip()
        elif first_line.startswith(self.FEEDBACK_NEUTRAL_PREFIX.rstrip()):
            label_start = first_line[len(self.FEEDBACK_NEUTRAL_PREFIX.rstrip()):].strip()
        else:
            label_start = ""

        label = [label_start] if label_start else []
        
        for line in block[1:]:
            label.append(line.strip())

        return {
            "type": "correct" if first_line.startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip()) else "incorrect" if first_line.startswith(self.FEEDBACK_WRONG_PREFIX.rstrip()) else "neutral",
            "feedback": label or [""],  # For no-input, the label is also the feedback
        }
    
    def _parse_general_raw(self, general_raw: List[str], feedback: Dict) -> Dict[str, List[str]]:
        """Parse general feedback for multiple-select questions."""
        general = {}
        # find the feedback sections based on the prefixes
        starts = [i for i, line in enumerate(general_raw)
                    if line.rstrip().startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip())
                    or line.rstrip().startswith(self.FEEDBACK_WRONG_PREFIX.rstrip())
                    or line.rstrip().startswith(self.FEEDBACK_NEUTRAL_PREFIX.rstrip())
                    or line.rstrip().startswith(self.FEEDBACK_SHOW_ANSWER_PREFIX.rstrip())
                    or line.rstrip().startswith(self.QUESTION_STRUCTURE_PREFIX.rstrip())
                    ]
        question_raw = []
        correct_raw = []
        incorrect_raw = []
        show_answer_raw = []
        mixed_raw = []
        # loop over starting positions and assign feedback to the appropriate section based on the prefix
        for idx, start in enumerate(starts):
            end = starts[idx + 1] if idx + 1 < len(starts) else len(general_raw)
            block = general_raw[start:end]
            prefix = block[0].rstrip()[:1]
            content = list(block)  # make a copy of the block
            content[0] = content[0].strip()[2:]  # Remove prefix from first line
            if prefix == self.FEEDBACK_CORRECT_PREFIX[0]:
                correct_raw.extend(content)
            elif prefix == self.FEEDBACK_WRONG_PREFIX[0]:
                incorrect_raw.extend(content)
            elif prefix == self.FEEDBACK_NEUTRAL_PREFIX[0]:
                mixed_raw.extend(content)
            elif prefix == self.FEEDBACK_SHOW_ANSWER_PREFIX[0]:
                show_answer_raw.extend(content)
            elif prefix == self.QUESTION_STRUCTURE_PREFIX[0]:
                question_raw.extend(content)
        # fill empty sections with default feedback if not provided
        general['correct'] = correct_raw if correct_raw else feedback['correct']
        general['incorrect'] = incorrect_raw if incorrect_raw else feedback['incorrect']
        general['mixed'] = mixed_raw if mixed_raw else feedback['mixed']
        general['question'] = question_raw # no default for question, as it is required to provide a question structure in gaps
        general['show-answer'] = show_answer_raw if show_answer_raw else feedback['show-answer']

        return general
    
    def _handle_short_answer_gaps(self, node: Node, node_id: str, feedback: Dict, columns: str) -> List[Node]:
        """Handle short-answer gaps questions."""
        pre_text, options_raw, general_raw, post_text = self._split_input()

        # Add pre-text if present
        self._add_text_section(node, node_id, pre_text, "pretext")

        # Parse options
        options_data = self._parse_short_answer_options(options_raw, feedback, node_id)

        # Do something with the options and the general_raw part
        if not general_raw:
            raise ValueError(
                f"Question variant short-answer of type gaps at line "
                f"{self.lineno} in {self.env.docname} is malformed. "
                f"Please provide a section starting with '{self.GENERAL_FEEDBACK_SEPARATOR}' "
                f"between '{self.SEPARATOR}' and '{self.SEPARATOR}'."
            )
        general = self._parse_general_raw(general_raw, feedback)
        if not general['question']:
            raise ValueError(
                f"Question variant short-answer of type gaps at line "
                f"{self.lineno} in {self.env.docname} is malformed. "
                f"Please provide a question by including at least one line "
                f"starting with '{self.QUESTION_STRUCTURE_PREFIX}' "
                f"in the section starting with '{self.GENERAL_FEEDBACK_SEPARATOR}'."
            )
        # count the number of gaps and match with the number of options
        gaps_starts = []
        for line in general['question']:
            this_line_starts = [m.start() for m in re.finditer(r"\{gap\}", line)]
            gaps_starts.extend(this_line_starts)
        if len(gaps_starts) != len(options_data):
            raise ValueError(
                f"Question variant short-answer of type gaps at line "
                f"{self.lineno} in {self.env.docname} is malformed. "
                f"The number of gaps indicated by '{{gap}}' in the question "
                f"does not match the number of options provided. Found "
                f"{len(gaps_starts)} gaps and {len(options_data)} options."
            )
        # Replace {gap} placeholders with empty inline cards
        general['question'] = [line.replace("{gap}", "{inline-card}`Body <Footer>`") for line in general['question']]
        
        # Use a plain docutils container for question text and inline fields.
        # This avoids any directive-generated wrappers that could render as a card.
        question_section = nodes.section(
            classes=["question-text"],
            ids=[f"{node_id}-question"]
        )
        target_container = nodes.container(classes=["question", "question-surface"])
        question_section += target_container
        node += question_section
        self.state.nested_parse(
            general['question'], self.content_offset, target_container
        )
        # Find all inline cards and populate them with the corresponding options
        list_of_cards = target_container.findall(inline_card)
        for idx, card in enumerate(list_of_cards):
            card.classes = [f"field-{idx} field"] + card.classes
            option = options_data[idx]
            # Add input field to body
            body = card.next_node(inline_card_body)
            if body is None:
                body = inline_card_body()
            body.clear() # remove dummy content
            body.classes = [f"field-{idx} field"] + body.classes
            if option["type"][0] == "T":
                input_html = (
                    f"<input type=\"text\" class='question-option-input type-{option['type']}' "
                    f"id='{node_id}-option-{idx}-input' "
                    f"placeholder='Answer...'></input>"
                )
            elif option["type"][0] == "M":
                evalf_attr = option.get("evalf", "no")
                input_html = (
                    f"<math-field class='question-option-input type-{option['type']}' "
                    f"id='{node_id}-option-{idx}-input' "
                    f"data-evalf='{evalf_attr}' "
                    f"placeholder='\\text{{Answer...}}'>"
                    f"</math-field>"
                )
            elif option["type"][0:2] == "DS":
                replace_answer = []
                input_html = (
                    f"<select class='question-option-input type-{option['type']} default-selected' "
                    f"id='{node_id}-option-{idx}-input'>"
                    f"<option class='default' id='{node_id}-option-{idx}-default' disabled selected hidden>Answer...</option>"
                )
                for ans in re.split(r'(?<!\\);', option["answer"]):
                    # check if answer is contained in { and }, and if so, only take the content within the brackets as the answer text, to allow for semicolons in the answer text by escaping them with a backslash
                    if ans.strip().startswith("{") and ans.strip().endswith("}"):
                        ans = ans.strip()[1:-1]
                        correct = True
                        replace_answer.append(ans)
                    else:
                        correct = False
                    ans_clean = ans.strip().replace('\\;', ';').replace('\\{', '{').replace('\\}', '}')
                    input_html += f"<option>{ans_clean}</option>"
                input_html += "</select>"
                option["answer"] = " ; ".join(replace_answer)
            body += nodes.raw(input_html, input_html, format="html")
            # now take the footer of the card and populate it with the corresponding feedback
            footer = card.next_node(inline_card_footer)
            if footer is None:
                footer = inline_card_footer()
            footer.clear() # remove dummy content
            footer.classes = [f"field-{idx} field"] + footer.classes
            # correct feedback for this field
            correct_feedback = option["correct_feedback"][0] # always take only the first line
            correct_node = inline_card_feedback()
            correct_node.classes = ["correct", f"field-{idx} field"]
            correct_nodes, _ = self.state.inline_text(correct_feedback, self.lineno)
            correct_node.extend(correct_nodes)
            footer += correct_node
            # incorrect feedback for this field
            incorrect_feedback = option["incorrect_feedback"][0] # always take only the first line
            incorrect_node = inline_card_feedback()
            incorrect_node.classes = ["incorrect", f"field-{idx} field"]
            incorrect_nodes, _ = self.state.inline_text(incorrect_feedback, self.lineno)
            incorrect_node.extend(incorrect_nodes)
            footer += incorrect_node
            # show-answer feedback for this field
            show_answer_feedback = option["show_answer_feedback"][0] # always take only the first line
            show_answer_node = inline_card_feedback()
            show_answer_node.classes = ["show-answer", f"field-{idx} field"]
            show_answer_nodes, _ = self.state.inline_text(show_answer_feedback, self.lineno)
            show_answer_node.extend(show_answer_nodes)
            footer += show_answer_node
            # parsing error feedback for this field
            parsing_error_feedback = "Parsing error."
            parsing_error_node = inline_card_feedback()
            parsing_error_node.classes = ["parsing-error", f"field-{idx} field"]
            parsing_error_nodes, _ = self.state.inline_text(parsing_error_feedback, self.lineno)
            parsing_error_node.extend(parsing_error_nodes)
            footer += parsing_error_node
            # # add correct answer to the footer for show answer functionality
            answer = option["answer"]
            answer_node = inline_card_feedback()
            answer_node.classes = ["answer", f"field-{idx} field"]
            answer_nodes, _ = self.state.inline_text("_placeholder_", self.lineno)
            answer_nodes[0] = nodes.Text(answer) # replace the placeholder text with the actual answer
            answer_node.extend(answer_nodes)
            footer += answer_node

        # Add post-text if present
        self._add_text_section(node, node_id, post_text, "posttext")

        # Add overall feedback section
        feedback_section = nodes.section(
            classes=["question-feedback", "overall-feedback"],
            ids=[f"{node_id}-overall-feedback"]
        )
        feedback_grid = [
            "::::{grid} 1",
            ":gutter: 3",
            "",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: correct",
            ":class-body: correct",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: incorrect",
            ":class-body: incorrect",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: mixed",
            ":class-body: mixed",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: show-answer",
            ":class-body: show-answer",
            "",
            ":::",
            "::::",
        ]
        self.state.nested_parse(feedback_grid, self.content_offset, feedback_section)
        # loop over the 4 feedback cards and populate them with the appropriate general feedback
        card = 0
        for container in feedback_section.findall(nodes.container):
            card_classes = container.get("classes", [])
            if "sd-card-body" in card_classes:
                card += 1
            else:
                continue
            if "correct" in card_classes:
                feedback_content = general['correct']
            elif "incorrect" in card_classes:
                feedback_content = general['incorrect']
            elif "mixed" in card_classes:
                feedback_content = general['mixed']
            elif "show-answer" in card_classes:
                feedback_content = general['show-answer']
            else:
                continue
            fb_sub_section = nodes.section(
                classes=["question-feedback", f"overall-feedback-{card}"],
                ids=[f"{node_id}-overall-feedback-{card}"]
            )
            self.state.nested_parse(feedback_content, self.content_offset, fb_sub_section)
            container += fb_sub_section
        node += feedback_section

        # Add buttons
        button_count = 3 if node["show_answer"] else 2
        buttons = [
            ("submit-button", "<i class='fa-solid fa-paper-plane'></i> Submit answer(s)"),
        ]
        if node["show_answer"]:
            buttons.append(("show-button", "<i class='fa-solid fa-file-circle-check'></i> Show answer(s)"))
        buttons.append(("reset-button", "<i class='fa-solid fa-repeat'></i> Try again"))

        self._add_button_section(node, node_id, buttons, node["show_answer"], button_count)

        return [node]

    def _handle_short_answer_blocks(self, node: Node, node_id: str, feedback: Dict, columns: str) -> List[Node]:
        """Handle short-answer block questions."""
        pre_text, options_raw, _, post_text = self._split_input()

        # Add pre-text if present
        self._add_text_section(node, node_id, pre_text, "pretext")

        # Parse options
        options_data = self._parse_short_answer_options(options_raw, feedback, node_id)
        
        # Render options as cards
        self._render_short_answer_cards(node, node_id, options_data, columns)

        # Add post-text if present
        self._add_text_section(node, node_id, post_text, "posttext")

        # Add buttons
        button_count = 3 if node["show_answer"] else 2
        buttons = [
            ("submit-button", "<i class='fa-solid fa-paper-plane'></i> Submit answer(s)"),
        ]
        if node["show_answer"]:
            buttons.append(("show-button", "<i class='fa-solid fa-file-circle-check'></i> Show answer(s)"))
        buttons.append(("reset-button", "<i class='fa-solid fa-repeat'></i> Try again"))

        self._add_button_section(node, node_id, buttons, node["show_answer"], button_count)

        return [node]

    def _parse_short_answer_options(
        self, options_raw: List[str], feedback: Dict, node_id: str
    ) -> List[Dict[str, Any]]:
        """Parse short-answer options from raw content."""
        if not options_raw:
            return []

        # Find option markers and validate mode tokens early.
        allowed_modes = {
            "T", "TI", "TF", "M", "MR", "MNR", "MAP", "MRP",
            "ME", "MRE", "MNRE", "MAPE", "MRPE", "DS",
        }
        option_starts = []
        for i, line in enumerate(options_raw):
            match = re.match(r"^([A-Za-z]+)\[", line.strip())
            if not match:
                continue
            mode = match.group(1)
            if mode not in allowed_modes:
                raise ValueError(
                    f"Unsupported short-answer mode '{mode}' at line {self.lineno + i} in "
                    f"{self.env.docname}."
                )
            option_starts.append(i)

        if not option_starts:
            raise ValueError(
                f"No valid short-answer options found at line {self.lineno} in "
                f"{self.env.docname}. Each option must start with one of "
                f"{sorted(allowed_modes)} followed by '['."
            )

        options = []
        for idx, start in enumerate(option_starts):
            end = option_starts[idx + 1] if idx + 1 < len(option_starts) else len(options_raw)
            block = options_raw[start:end]
            option = self._parse_single_short_answer_option(block, feedback)
            options.append(option)

        return options

    def _extract_evalf_from_answer(self, answer: str) -> Tuple[str, str]:
        """Extract optional evalf significant digits from answer syntax for E-modes.

        For E-modes, the significant digits must be provided as an extra trailing
        unescaped ';<digits>' entry.
        """
        parts = [part.strip() for part in re.split(r'(?<!\\);', answer)]
        if parts and parts[-1].isdigit() and int(parts[-1]) > 0:
            return ";".join(parts[:-1]), str(int(parts[-1]))
        else:
            raise ValueError(
                f"Invalid formatted digits at line {self.lineno} in {self.env.docname}. "
                f"Provide significant digits after the last unescaped ';' as an integer."
            )

    def _parse_single_short_answer_option(self, block: List[str], feedback: Dict) -> Dict[str, Any]:
        """Parse a single short-answer option."""
        first_line = block[0].rstrip()
        
        # Extract option type and answer
        raw_option_type = first_line.split("[")[0].strip()
        if "(" in raw_option_type or ")" in raw_option_type:
            raise ValueError(
                f"Malformed mode '{raw_option_type}' at line {self.lineno} in {self.env.docname}."
            )

        allowed_base_modes = {"T", "TI", "TF", "M", "MR", "MNR", "MAP", "MRP", "DS"}
        e_modes = {"ME", "MRE", "MNRE", "MAPE", "MRPE"}

        answer_str_raw = first_line.split("[")[1].split("]")[0].strip()
        if raw_option_type in e_modes:
            option_type = raw_option_type[:-1]
            answer_str, evalf = self._extract_evalf_from_answer(answer_str_raw)
            if answer_str.strip() == "":
                raise ValueError(
                    f"Malformed answer for mode '{raw_option_type}' at line {self.lineno} in "
                    f"{self.env.docname}. Provide an answer before optional significance digits."
                )
        else:
            option_type = raw_option_type
            answer_str = answer_str_raw
            evalf = "no"

        if option_type not in allowed_base_modes:
            raise ValueError(
                f"Unsupported short-answer mode '{raw_option_type}' at line {self.lineno} in "
                f"{self.env.docname}."
            )
        
        # Extract label (text after ] on first line and subsequent lines until feedback)
        label_start = first_line.split("]", 1)[1].strip()
        label = [label_start] if label_start else []
        
        line_idx = 1
        while line_idx < len(block):
            line = block[line_idx].strip()
            if line.startswith(self.FEEDBACK_WRONG_PREFIX.rstrip()) or line.startswith(
                self.FEEDBACK_CORRECT_PREFIX.rstrip()) or line.startswith(self.FEEDBACK_SHOW_ANSWER_PREFIX.rstrip()):
                break
            label.append(line)
            line_idx += 1

        # Extract feedback
        correct_fb = []
        incorrect_fb = []
        show_fb = []
        
        if line_idx < len(block):
            last_type = None
            while line_idx < len(block):
                line = block[line_idx].rstrip()
                if line.startswith(self.FEEDBACK_WRONG_PREFIX.rstrip()):
                    if incorrect_fb:
                        incorrect_fb.append("")
                    incorrect_fb.append(line[2:])
                    last_type = "incorrect"
                elif line.startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip()):
                    if correct_fb:
                        correct_fb.append("")
                    correct_fb.append(line[2:])
                    last_type = "correct"
                elif line.startswith(self.FEEDBACK_SHOW_ANSWER_PREFIX.rstrip()):
                    if show_fb:
                        show_fb.append("")
                    show_fb.append(line[2:])
                    last_type = "show"
                else:
                    if last_type == "incorrect":
                        incorrect_fb.append(line)
                    elif last_type == "correct":
                        correct_fb.append(line)
                    elif last_type == "show":
                        show_fb.append(line)
                line_idx += 1
        # Set defaults if not provided
        if not correct_fb:
            correct_fb = feedback[True]
        if not incorrect_fb:
            incorrect_fb = feedback[False]
        if not show_fb:
            show_fb = correct_fb  # Default show answer feedback is the same as correct feedback

        return {
            "type": option_type,
            "evalf": evalf,
            "answer": answer_str,
            "label": label or [""],
            "correct_feedback": correct_fb,
            "incorrect_feedback": incorrect_fb,
            "show_answer_feedback": show_fb,
        }

    def _render_short_answer_cards(self, node: Node, node_id: str, options: List[Dict], columns: str) -> None:
        """Render short-answer options as cards."""
        # Create card markup
        cards_markup = [
            f"::::{{grid}} {columns}",
            ":gutter: 3",
            "",
        ]
        for option in options:
            label = option["label"]
            cards_markup.append(":::{grid-item-card}")
            cards_markup.append(":shadow: lg")
            cards_markup.append(":width: 100%")
            cards_markup.append(":class-card: option")
            cards_markup.append(":class-body: input")
            if label == [""]:
                cards_markup.append(":class-header: hidden")
            cards_markup.extend(["^^^", "+++", ":::"])
        cards_markup.append("::::")

        # Render cards
        options_section = nodes.section(
            classes=["question-options"],
            ids=[f"{node_id}-options"]
        )
        self.state.nested_parse(cards_markup, self.content_offset, options_section)
        node += options_section

        # Populate card content
        current_card = -1
        for container in options_section.findall(nodes.container):
            card_classes = container.get("classes", [])
            
            if "sd-card-header" in card_classes:
                current_card += 1
                option = options[current_card]
                label_section = nodes.section(
                    classes=["question-option-label"],
                    ids=[f"{node_id}-option-{current_card}-label"]
                )
                self.state.nested_parse(
                    option["label"], self.content_offset, label_section
                )
                container += label_section
                
            elif "sd-card-body" in card_classes:
                option = options[current_card]
                
                # Add input field
                if option["type"][0] == "T":
                    input_html = (
                        f"<textarea class='question-option-input type-{option['type']}' "
                        f"id='{node_id}-option-{current_card}-input' "
                        f"placeholder='Insert your answer here...'></textarea>"
                    )
                elif option["type"][0] == "M":
                    evalf_attr = option.get("evalf", "no")
                    input_html = (
                        f"<math-field class='question-option-input type-{option['type']}' "
                        f"id='{node_id}-option-{current_card}-input' "
                        f"data-evalf='{evalf_attr}' "
                        f"placeholder='\\text{{Insert your answer here...}}'>"
                        f"</math-field>"
                    )
                container += nodes.raw(input_html, input_html, format="html")
                
                # Add answer (hidden)
                answer_section = nodes.section(
                    classes=["question-option-answer"],
                    ids=[f"{node_id}-option-{current_card}-answer"]
                )
                answer_section += nodes.paragraph(text=option["answer"])
                container += answer_section
                
            elif "sd-card-footer" in card_classes:
                option = options[current_card]
                
                # Add correct feedback
                correct_section = nodes.section(
                    classes=["question-feedback", "correct"],
                    ids=[f"{node_id}-option-{current_card}-feedback"]
                )
                self.state.nested_parse(
                    option["correct_feedback"], self.content_offset, correct_section
                )
                container += correct_section
                
                # Add incorrect feedback
                incorrect_section = nodes.section(
                    classes=["question-feedback", "incorrect"],
                    ids=[f"{node_id}-option-{current_card}-feedback-incorrect"]
                )
                self.state.nested_parse(
                    option["incorrect_feedback"], self.content_offset, incorrect_section
                )
                container += incorrect_section

                # Add show answer feedback
                show_answer_section = nodes.section(
                    classes=["question-feedback", "show-answer"],
                    ids=[f"{node_id}-option-{current_card}-feedback-show-answer"]
                )
                self.state.nested_parse(
                    option["show_answer_feedback"], self.content_offset, show_answer_section
                )
                container += show_answer_section

                # Add parsing error feedback (for cases where answer can't be parsed, e.g. invalid math input)
                error_section = nodes.section(
                    classes=["question-feedback", "parsing-error"],
                    ids=[f"{node_id}-option-{current_card}-feedback-parsing-error"]
                )
                self.state.nested_parse(
                    [r"We couldn't parse your answer. You most likely made a mistake in the $\LaTeX$ syntax."], self.content_offset, error_section
                )
                container += error_section

    def _handle_multiple_choice_shared(
        self, node: Node, node_id: str, columns: str, feedback: Dict
    ) -> Node:
        """Shared logic for multiple-choice question types."""
        pre_text, options_raw, general_raw, post_text = self._split_input()

        # Parse options
        options = self._parse_multiple_choice_options(options_raw, feedback)

        # Validate (single-select requires at least one correct answer)
        if node["variant"] == "single-select" and not any(opt["is_correct"] for opt in options):
            raise ValueError(
                f"No correct options provided for single-select question at line "
                f"{self.lineno} in {self.env.docname}. Please provide at least one "
                f"correct option."
            )

        # Add pre-text
        self._add_text_section(node, node_id, pre_text, "pretext")

        # Render options as cards
        self._render_multiple_choice_cards(node, node_id, options, columns)

        # Add post-text
        self._add_text_section(node, node_id, post_text, "posttext")

        return node, general_raw

    def _parse_multiple_choice_options(
        self, options_raw: List[str], feedback: Dict
    ) -> List[Dict[str, Any]]:
        """Parse multiple-choice options from raw content."""
        if not options_raw:
            return []

        # Find option markers
        option_starts = [
            i for i, line in enumerate(options_raw)
            if line.rstrip().startswith(self.OPTION_CHECKBOX_UNCHECKED) or
            line.rstrip().startswith(self.OPTION_CHECKBOX_CHECKED)
        ]

        options = []
        for idx, start in enumerate(option_starts):
            end = option_starts[idx + 1] if idx + 1 < len(option_starts) else len(options_raw)
            block = options_raw[start:end]
            option = self._parse_single_multiple_choice_option(block, feedback)
            options.append(option)

        return options

    def _parse_single_multiple_choice_option(
        self, block: List[str], feedback: Dict
    ) -> Dict[str, Any]:
        """Parse a single multiple-choice option."""
        first_line = block[0].rstrip()
        is_correct = first_line[1] == "x"
        
        # Extract option content, feedback and "show answer" feedback
        fb_starts = [
            i for i, line in enumerate(block)
            if line.rstrip().startswith(self.FEEDBACK_WRONG_PREFIX.rstrip())
        ]
        fb_show = [
            i for i, line in enumerate(block)
            if line.rstrip().startswith(self.FEEDBACK_SHOW_ANSWER_PREFIX.rstrip())
        ]

        if fb_starts and not fb_show:
            # only regular feedback provided
            # use regular feedback for both regular and show answer feedback
            fb_start = fb_starts[0]
            option_content = block[:fb_start]
            option_content[0] = option_content[0].rstrip()[3:].strip()  # Remove [ ] or [x]
            option_feedback = block[fb_start:]
            option_feedback[0] = option_feedback[0].rstrip()[2:].strip()  # Remove "> "
            option_show_answer_feedback = option_feedback
        elif fb_show and not fb_starts:
            # only show answer feedback provided
            # use default feedback for regular feedback
            fb_show_start = fb_show[0]
            option_content = block[:fb_show_start]
            option_content[0] = option_content[0].rstrip()[3:].strip()  # Remove [ ] or [x]
            option_feedback = feedback[is_correct]
            option_show_answer_feedback = block[fb_show_start:]
            option_show_answer_feedback[0] = option_show_answer_feedback[0].rstrip()[2:].strip()  # Remove "& "
        elif fb_starts and fb_show:
            # both regular and show answer feedback provided
            # order might be mixed, so determine which comes first
            fb_start = fb_starts[0]
            fb_show_start = fb_show[0]
            if fb_start < fb_show_start:
                # regular feedback comes first
                option_content = block[:fb_start]
                option_content[0] = option_content[0].rstrip()[3:].strip()  # Remove [ ] or [x]
                option_feedback = block[fb_start:fb_show_start]
                option_feedback[0] = option_feedback[0].rstrip()[2:].strip()  # Remove "> "
                option_show_answer_feedback = block[fb_show_start:]
                option_show_answer_feedback[0] = option_show_answer_feedback[0].rstrip()[2:].strip()  # Remove "& "
            else:
                # show answer feedback comes first
                option_content = block[:fb_show_start]
                option_content[0] = option_content[0].rstrip()[3:].strip()  # Remove [ ] or [x]
                option_show_answer_feedback = block[fb_show_start:fb_start]
                option_show_answer_feedback[0] = option_show_answer_feedback[0].rstrip()[2:].strip()  # Remove "& "
                option_feedback = block[fb_start:]
                option_feedback[0] = option_feedback[0].rstrip()[2:].strip()  # Remove "> "
        else:
            # no regular or show answer feedback provided, use default feedback twice
            option_content = block
            option_content[0] = option_content[0].rstrip()[3:].strip()  # Remove [ ] or [x]
            option_feedback = feedback[is_correct]
            option_show_answer_feedback = option_feedback

        return {
            "is_correct": is_correct,
            "content": option_content,
            "feedback": option_feedback,
            "show": option_show_answer_feedback,
        }

    def _render_multiple_choice_cards(
        self, node: Node, node_id: str, options: List[Dict], columns: str
    ) -> None:
        """Render multiple-choice options as cards."""
        # Create card grid markup
        cards_markup = [
            f"::::{{grid}} {columns}",
            ":gutter: 3",
            "",
        ]
        for _ in options:
            cards_markup.extend([
                ":::{grid-item-card}",
                ":shadow: lg",
                ":class-card: option",
                "+++",
                ":::",
            ])
        cards_markup.append("::::")

        # Render cards
        options_section = nodes.section(
            classes=["question-options"],
            ids=[f"{node_id}-options"]
        )
        self.state.nested_parse(cards_markup, self.content_offset, options_section)
        node += options_section

        # icon style
        if node["variant"] == "single-select":
            icon = "circle"
        else:  # multiple-select
            icon = "square"

        # Populate card content
        current_card = -1
        for container in options_section.findall(nodes.container):
            card_classes = container.get("classes", [])
            
            if "sd-card-body" in card_classes:
                current_card += 1
                option = options[current_card]
                option_section = nodes.section(
                    classes=["question-option"],
                    ids=[f"{node_id}-option-{current_card}"]
                )
                self.state.nested_parse(
                    option["content"], self.content_offset, option_section
                )
                first_child = option_section[0] if option_section else None
                icon_html = f"<i class='fa-regular fa-{icon} off'></i><i class='fa-solid fa-{icon}-check on'></i>&nbsp;"
                if first_child and isinstance(first_child, nodes.paragraph):
                    # add an icon to the first paragraph
                    first_child.insert(0, nodes.raw(icon_html, icon_html, format="html"))
                else:
                    # add the icon in a new div at the top of the option section
                    icon_html = "<div class='option-icon'>" + icon_html + "</div>"
                    option_section.insert(0, nodes.raw(icon_html, icon_html, format="html"))
                container += option_section
            elif "sd-card-footer" in card_classes:
                option = options[current_card]
                # regular feedback
                feedback_class = "correct" if option["is_correct"] else "incorrect"
                feedback_section = nodes.section(
                    classes=["question-feedback", feedback_class],
                    ids=[f"{node_id}-feedback-{current_card}"]
                )
                self.state.nested_parse(
                    option["feedback"], self.content_offset, feedback_section
                )
                feedback_section["data-correct"] = option["is_correct"]
                container += feedback_section
                # show answer feedback
                show_section = nodes.section(
                    classes=["question-show", feedback_class],
                    ids=[f"{node_id}-show-{current_card}"]
                )
                self.state.nested_parse(
                    option["show"], self.content_offset, show_section
                )
                feedback_section["data-correct"] = option["is_correct"]
                container += show_section

    def _handle_multiple_choice_single_select(
        self, node: Node, node_id: str, columns: str, feedback: Dict
    ) -> List[Node]:
        """Handle single-select multiple-choice questions."""
        node, _ = self._handle_multiple_choice_shared(node, node_id, columns, feedback)

        # Add buttons
        button_count = 2 if node["show_answer"] else 1
        buttons = []
        if node["show_answer"]:
            buttons.append(("show-button", "<i class='fa-solid fa-file-circle-check'></i> Show answer(s)"))
        buttons.append(("reset-button", "<i class='fa-solid fa-repeat'></i> Try again"))

        self._add_button_section(node, node_id, buttons, node["show_answer"], button_count)

        return [node]

    def _handle_multiple_choice_multiple_select(
        self, node: Node, node_id: str, columns: str, feedback: Dict
    ) -> List[Node]:
        """Handle multiple-select multiple-choice questions."""
        node, general_raw = self._handle_multiple_choice_shared(node, node_id, columns, feedback)

        # split general feedback into 4 sections based on prefixes
        if general_raw:
            general_feedback = {}
            # find the feedback sections based on the prefixes
            starts = [i for i, line in enumerate(general_raw)
                      if line.rstrip().startswith(self.FEEDBACK_CORRECT_PREFIX.rstrip())
                      or line.rstrip().startswith(self.FEEDBACK_WRONG_PREFIX.rstrip())
                      or line.rstrip().startswith(self.FEEDBACK_NEUTRAL_PREFIX.rstrip())
                      or line.rstrip().startswith(self.FEEDBACK_SHOW_ANSWER_PREFIX.rstrip())]
            correct_raw = []
            incorrect_raw = []
            missed_raw = []
            incorrect_missed_raw = []
            # loop over starting positions and assign feedback to the appropriate section based on the prefix
            for idx, start in enumerate(starts):
                end = starts[idx + 1] if idx + 1 < len(starts) else len(general_raw)
                block = general_raw[start:end]
                prefix = block[0].rstrip()[:1]
                content = list(block)  # make a copy of the block
                content[0] = content[0].rstrip()[2:].strip()  # Remove prefix from first line
                if prefix == self.FEEDBACK_CORRECT_PREFIX[0]:
                    correct_raw.extend(content)
                elif prefix == self.FEEDBACK_WRONG_PREFIX[0]:
                    incorrect_raw.extend(content)
                elif prefix == self.FEEDBACK_NEUTRAL_PREFIX[0]:
                    missed_raw.extend(content)
                elif prefix == self.FEEDBACK_SHOW_ANSWER_PREFIX[0]:
                    incorrect_missed_raw.extend(content)
            # fill empty sections with default feedback if not provided
            general_feedback['correct'] = correct_raw if correct_raw else feedback['correct']
            general_feedback['incorrect'] = incorrect_raw if incorrect_raw else feedback['incorrect']
            general_feedback['missed'] = missed_raw if missed_raw else feedback['missed']
            general_feedback['incorrect_missed'] = incorrect_missed_raw if incorrect_missed_raw else feedback['incorrect-missed']
        else: # default to using the same feedback for all 4 sections if general feedback is not provided
            general_feedback = {
                'correct': feedback["correct"],
                'incorrect': feedback["incorrect"],
                'missed': feedback["missed"],
                'incorrect_missed': feedback["incorrect-missed"]
            }

        # Add overall feedback section
        feedback_section = nodes.section(
            classes=["question-feedback", "overall-feedback"],
            ids=[f"{node_id}-overall-feedback"]
        )
        feedback_grid = [
            "::::{grid} 1",
            ":gutter: 3",
            "",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: correct",
            ":class-body: correct",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: incorrect",
            ":class-body: incorrect",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: missed",
            ":class-body: missed",
            "",
            ":::",
            ":::{grid-item-card}",
            ":shadow: lg",
            ":class-card: incorrect-missed",
            ":class-body: incorrect-missed",
            "",
            ":::",
            "::::",
        ]
        self.state.nested_parse(feedback_grid, self.content_offset, feedback_section)
        # loop over the 4 feedback cards and populate them with the appropriate general feedback
        card = 0
        for container in feedback_section.findall(nodes.container):
            card_classes = container.get("classes", [])
            if "sd-card-body" in card_classes:
                card += 1
            else:
                continue
            if "correct" in card_classes:
                feedback_content = general_feedback['correct']
            elif "incorrect" in card_classes:
                feedback_content = general_feedback['incorrect']
            elif "missed" in card_classes:
                feedback_content = general_feedback['missed']
            elif "incorrect-missed" in card_classes:
                feedback_content = general_feedback['incorrect_missed']
            else:
                continue
            fb_sub_section = nodes.section(
                classes=["question-feedback", f"overall-feedback-{card}"],
                ids=[f"{node_id}-overall-feedback-{card}"]
            )
            self.state.nested_parse(feedback_content, self.content_offset, fb_sub_section)
            container += fb_sub_section
        node += feedback_section

        # Add buttons
        button_count = 3 if node["show_answer"] else 2
        buttons = [
            ("submit-button", "<i class='fa-solid fa-paper-plane'></i> Submit answer(s)"),
        ]
        if node["show_answer"]:
            buttons.append(("show-button", "<i class='fa-solid fa-file-circle-check'></i> Show answer(s)"))
        buttons.append(("reset-button", "<i class='fa-solid fa-repeat'></i> Try again"))

        self._add_button_section(node, node_id, buttons, node["show_answer"], button_count)

        return [node]

class question_node(nodes.Admonition, nodes.Element):
    """Custom node for question directives."""
    pass


def visit_question_node(self, node: question_node) -> None:
    """Visit handler for question nodes."""
    css_classes = " ".join(node["class"])
    css_classes += f" {node['type']} {node['variant']}"
    
    tag_name = "div"
    if node["admonition"]:
        css_classes = f"admonition {css_classes}"
    
    self.body.append(self.starttag(node, tag_name, CLASS=css_classes, ids=node["ids"]))


def depart_question_node(self, node: question_node) -> None:
    """Depart handler for question nodes."""
    if not node["nocaption"]:
        node_id = node.attributes.get("ids", [""])[0]
        search_str = f'<p class="admonition-title" id="{node_id}-title">'
        idx = _find_last_index(self.body, search_str)
        if idx >= 0:
            element = '<span class="caption-number">Question </span>'
            self.body.insert(idx + 1, element)
    # if the question is NOT rendered as an admonition,
    # the title paragraph should not have the class "admonition-title"
    # so replace it with "question-title" to allow styling. 
    if not node["admonition"]:
        node_id = node.attributes.get("ids", [""])[0]
        search_str = f'<p class="admonition-title" id="{node_id}-title">'
        target_str = f'<p class="question-title" id="{node_id}-title">'
        self.body = [line.replace(search_str, target_str) for line in self.body]
    self.body.append("</div>")


def _find_last_index(lst: List[str], value: str, skip: int = 0) -> int:
    """Find the last occurrence of a value in a list, optionally skipping occurrences.
    
    Args:
        lst: The list to search
        value: The value to find
        skip: Number of occurrences to skip from the end
        
    Returns:
        The index of the occurrence, or -1 if not found
    """
    skip_count = skip
    for i in reversed(range(len(lst))):
        if lst[i] == value:
            if skip_count == 0:
                return i
            skip_count -= 1
    return -1


def setup(app) -> Dict[str, Any]:
    """Setup function for Sphinx extension."""
    app.add_directive("question", QuestionDirective)
    app.add_node(question_node, html=(visit_question_node, depart_question_node))
    
    # Add CSS and JavaScript files
    app.add_css_file("teachbooks_questions.css")
    app.add_css_file("inline-card.css")
    js_files = [
        "https://cdn.jsdelivr.net/npm/mathlive",
        "teachbooks_wrapadmonition.js",
        "teachbooks_mcss.js",
        "teachbooks_mcms.js",
        "teachbooks_nins.js",
        "teachbooks_fix_mathfield.js",
    ]
    for js_file in js_files:
        app.add_js_file(js_file)
    app.add_js_file("teachbooks_sab.js",
        type="module"
    )
    app.add_js_file("teachbooks_sag.js",
        type="module"
    )
    app.add_js_file("teachbooks_math_utils.js",
        type="module"
    )
    
    # Add static files path
    static_path = os.path.join(os.path.dirname(__file__), "_static")
    app.config.html_static_path.append(static_path)

    # Register inline card and nodes
    app.add_role("inline-card", inline_card_role)
    app.add_node(
        inline_card,
        html=(visit_inline_card_html, depart_inline_card_html),
    )
    app.add_node(
        inline_card_body,
        html=(visit_inline_card_body_html, depart_inline_card_body_html),
    )
    app.add_node(
        inline_card_footer,
        html=(visit_inline_card_footer_html, depart_inline_card_footer_html),
    )
    app.add_node(
        inline_card_feedback,
        html=(visit_inline_card_feedback_html, depart_inline_card_feedback_html),
    )
    
    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


from docutils import nodes
from docutils.parsers.rst import roles


# ----------------------------
# Node definitions
# ----------------------------

class inline_card(nodes.Inline, nodes.Element):
    """Container node for the inline card."""
    classes = []


class inline_card_body(nodes.Inline, nodes.Element):
    """Body part."""
    classes = []


class inline_card_footer(nodes.Inline, nodes.Element):
    """Footer part."""
    classes = []

class inline_card_feedback(nodes.Inline, nodes.Element):
    """Feedback part."""
    classes = []


# ----------------------------
# Role implementation
# ----------------------------

def _is_escaped(text: str, index: int) -> bool:
    """Return whether the character at index is escaped by a backslash."""
    backslash_count = 0
    current_index = index - 1
    while current_index >= 0 and text[current_index] == "\\":
        backslash_count += 1
        current_index -= 1
    return backslash_count % 2 == 1


def _split_inline_card_text(text: str) -> Tuple[str, str | None]:
    """Split inline-card text into body and an optional trailing footer.

    The footer is recognized only when the role content ends with an
    unescaped ``>`` that matches an earlier unescaped ``<``. Nested angle
    brackets inside the footer are supported so other roles can be used in
    the footer text.
    """
    end_index = len(text) - 1
    while end_index >= 0 and text[end_index].isspace():
        end_index -= 1

    if end_index < 0 or text[end_index] != ">" or _is_escaped(text, end_index):
        return text, None

    depth = 1
    start_index = None
    for current_index in range(end_index - 1, -1, -1):
        current_char = text[current_index]
        if current_char not in "<>":
            continue
        if _is_escaped(text, current_index):
            continue
        if current_char == ">":
            depth += 1
            continue

        depth -= 1
        if depth == 0:
            start_index = current_index
            break

    if start_index is None:
        return text, None

    if start_index > 0 and not text[start_index - 1].isspace():
        return text, None

    body_text = text[:start_index].rstrip().replace("\\>", ">").replace("\\<", "<")
    footer_text = text[start_index + 1:end_index].strip().replace("\\>", ">").replace("\\<", "<")

    return body_text, footer_text or None

def inline_card_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    options = options or {}

    # Split BodyText and optional <FooterText>
    body_text, footer_text = _split_inline_card_text(text)
    body_text = body_text.strip()

    # Main container
    card = inline_card()

    # ---- Body ----
    body_node = inline_card_body()
    body_children, body_messages = inliner.parse(
        body_text, lineno, inliner, body_node
    )
    body_node += body_children
    card += body_node

    # ---- Footer (optional) ----
    if footer_text:
        footer_node = inline_card_footer()
        footer_children, footer_messages = inliner.parse(
            footer_text, lineno, inliner, footer_node
        )
        footer_node += footer_children
        card += footer_node
    else:
        footer_messages = []

    return [card], body_messages + footer_messages



# ----------------------------
# HTML translators
# ----------------------------

def visit_inline_card_html(self, node):
    self.body.append(f'<span class="inline-card {" ".join(node.classes)}">')


def depart_inline_card_html(self, node):
    self.body.append('</span>')


def visit_inline_card_body_html(self, node):
    self.body.append(f'<span class="inline-card-body {" ".join(node.classes)}">')


def depart_inline_card_body_html(self, node):
    self.body.append('</span>')


def visit_inline_card_footer_html(self, node):
    self.body.append(f'<span class="inline-card-footer {" ".join(node.classes)}">')


def depart_inline_card_footer_html(self, node):
    self.body.append('</span>')

def visit_inline_card_feedback_html(self, node):
    self.body.append(f'<span class="inline-card-feedback {" ".join(node.classes)}">')

def depart_inline_card_feedback_html(self, node):
    self.body.append('</span>')