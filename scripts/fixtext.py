from typing import Any, Mapping, List, Union
import copy
import subprocess
import lxml.etree as ET
import proselint.config
import proselint.tools
import pyphen
from .xml_lib import get_all_text

def check_grammar(config: Any, text: str) -> None:
    errors = proselint.tools.lint(
        text,
        config=config["proselint_conf"],
    )
    if errors:
        lines = text.split("\n")
        for check, message, line_no, col_no, start, end, extent, severity, replacements in errors:
            line = lines[line_no]
            line = line[:start] + colored(line[start:end], "red") + line[end:]
            print("proselint:", check, message)
            print("in", line)
        if config["fatal"]:
            raise ValueError()

def check_spelling(config: Mapping[str, str], text: str) -> str:
    errors = []
    # TODO[2]: incorporate post-specific dictionary
    for line in subprocess.run(
        ["aspell", "pipe", "--dont-suggest", *config["args"]],
        input=text,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\n"):
        if line and line[0] not in {"*", "@"}:
            errors.append(line.strip())
    if errors:
        for error in errors:
            print("aspell:", error[2:])
        if config["fatal"]:
            raise ValueError()

def replace_symbols(text: str) -> str:
    text = text.replace("---", "—")
    text = text.replace("--", "–")
    text = text.replace("...", "…")
    text = text.replace("``", "“")
    text = text.replace("''", "”")
    text = text.replace("`", "‘")
    text = text.replace("'", "’")
    return text

def fix_text(
        context: Mapping[str, Any],
        elem: ET._Element,
        paragraph: bool = False
) -> List[Union[str, ET._Element]]:
    lang = elem.attrib["lang"].replace("-", "_")
    # hyphen_dict = pyphen.Pyphen(lang=lang)
    # TODO[2]: Decide what to do about hyphenation
    spelling_conf = {
        "args": [],
        "fatal": False,
    }
    grammar_conf = {
        "fatal": False,
        "proselint_conf": copy.deepcopy(proselint.config.default),
    }
    queue = [elem]
    while queue:
        this_elem = queue.pop()
        if this_elem.text is not None:
            this_elem.text = replace_symbols(this_elem.text)
            if paragraph:
                # this_elem.text = hyphen_dict.inserted(this_elem.text, hyphen="­")
                check_grammar(grammar_conf, this_elem.text)
            check_spelling(spelling_conf, this_elem.text)
        queue.extend(this_elem)
    return list(elem)

def fix_phrase(
        context: Mapping[str, Any],
        elem: ET._Element,
) -> List[Union[str, ET._Element]]:
    return fix_text(context, elem, paragraph=False)

def fix_para(
        context: Mapping[str, Any],
        elem: ET._Element,
) -> List[Union[str, ET._Element]]:
    return fix_text(context, elem, paragraph=True)
