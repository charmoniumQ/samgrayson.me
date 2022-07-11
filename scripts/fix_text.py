from typing import Any, Mapping, List, Union
import copy
from pathlib import Path
import subprocess
import tempfile
import lxml.etree as ET
import proselint.config
import proselint.tools
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
    with tempfile.TemporaryDirectory() as tmpdir:
        personal = (Path("/home/sam/Downloads") / "personal")
        personal.write_text("\n".join([
            " ".join(["personal_ws-1.1", config["shortlang"], str(len(config["allow_words"]))]),
            *config["allow_words"],
        ]))
        proc = subprocess.run(
            ["aspell", "pipe", "--dont-suggest", "--lang", config["lang"], "--personal", str(personal)],
            input=text,
            capture_output=True,
            text=True,
            check=True,
        )
    for line in proc.stdout.split("\n"):
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
        paragraph: bool = False,
) -> List[Union[str, ET._Element]]:
    lang = elem.attrib["lang"]
    shortlang = lang.partition("-")[0]
    spelling_conf = {
        "fatal": False,
        "lang": lang,
        "shortlang": shortlang,
        "allow_words": list(filter(bool, elem.attrib.get("allow_words", "").split(" "))),
    }
    grammar_conf = {
        "fatal": False,
        "proselint_conf": copy.deepcopy(proselint.config.default),
    }
    queue = [elem]
    split_text = []
    while queue:
        this_elem = queue.pop()
        if this_elem.text is not None:
            this_elem.text = replace_symbols(this_elem.text)
            split_text.append(this_elem.text)
        if this_elem.tail is not None:
            this_elem.tail = replace_symbols(this_elem.tail)
            split_text.append(this_elem.tail)
        queue.extend(this_elem)
    text = " ".join(split_text)
    check_spelling(spelling_conf, text)
    if paragraph:
        check_grammar(grammar_conf, text)
    return ([elem.text] if elem.text else []) + list(elem)

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
