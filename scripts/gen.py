import copy
from typing import Callable, Union, List, TypeVar, Any, cast, Mapping
from functools import partial
from pathlib import Path
import subprocess
import shutil
import xml.etree.ElementTree as ET
from xml.etree import ElementInclude

from termcolor import colored
import proselint.config, proselint.tools  # type: ignore
import pyphen  # type: ignore
import jinja2  # type: ignore
from slugify import slugify  # type: ignore

from .xml_lib import apply_to_tag, apply_to_text, make_element, inner_to_string, inner_text
from .util import compose_all

class ParseError(Exception):
    pass

def decode_bool(val: str, elem: ET.Element) -> bool:
    val = val.lower()
    if val == "true":
        return True
    elif val == "false":
        return False
    else:
        raise ParseError(f"Unable to decode {val} as bool in {elem.tag}")

T = TypeVar("T")

def config_and_apply_text(
        tag: str,
        config_func: Callable[[ET.Element], T],
        text_func: Callable[[T, str], str],
        elem: ET.Element,
) -> ET.Element:
    def apply_on_tag(elem: ET.Element) -> ET.Element:
        config = config_func(elem)
        # TODO: Remove tag as well
        return apply_to_text(partial(text_func, config), elem)
    return apply_to_tag(tag, apply_on_tag, elem)


def smarten_symbols_text(_: None, text: str) -> str:
    text = text.replace("---", "—")
    text = text.replace("--", "–")
    text = text.replace("...", "…")
    # TODO: smarten quotes
    return text

smarten_symbols = partial(
    config_and_apply_text,
    "smarten_symbols",
    lambda _: None,
    smarten_symbols_text,
)

class GrammarError(Exception):
    pass


# TODO: make check_* purely hierarchical

def check_grammar_para(config: Any, elem: ET.Element) -> ET.Element:
    text = inner_text(elem)
    errors = proselint.tools.lint(
        text,
        config=config,
    )
    if errors:
        lines = text.split("\n")
        for check, message, line_no, col_no, start, end, extent, severity, replacements in errors:
            line = lines[line_no]
            line = line[:start] + colored(line[start:end], "red") + line[end:]
            print(check, message)
            print(line)
        if config.get("fatal", True):
            raise GrammarError()
    return elem

def check_grammar_tag(elem: ET.Element) -> Any:
    config = copy.deepcopy(proselint.config.default)
    for key, val in elem.attrib.items():
        if key == "max_errors":
            config[key] == int(val)
        elif key.startswith("check."):
            config["checks"][key[len("check."):]] = decode_bool(val, elem)
        elif key == "fatal":
            config["fatal"] = decode_bool(val, elem)
        else:
            raise ParseError(f"Unknown attribute {key} in {elem}")
    return apply_to_tag("p", partial(check_grammar_para, config), elem)

check_grammar = partial(apply_to_tag, "check_grammar", check_grammar_tag)

def hyphenate_text(dic: pyphen.Pyphen, text: str) -> str:
    return cast(str, dic.inserted(text, hyphen="­"))

def hyphenate_config(elem: ET.Element) -> pyphen.Pyphen:
    lang = elem.attrib.get("lang", "en_US")
    return pyphen.Pyphen(lang=lang)

hyphenate = partial(
    config_and_apply_text,
    "hyphenate",
    hyphenate_config,
    hyphenate_text,
)

class SpellingError(Exception):
    pass

def check_spelling_text(config: Mapping[str, str], text: str) -> str:
    errors = []
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
            print(error)
        if config["fatal"]:
            raise SpellingError()
    return text

def check_spelling_config(elem: ET.Element) -> List[str]:
    return {
        "args": [
            *([f"--lang={elem.attrib['lang']}"] if "lang" in elem.attrib else []),
            *(
                [
                    f"--add-wordlists={wordlist}"
                    for wordlist in elem.attrib["wordlists"].split(",")
                ] if "wordlists" in elem.attrib else []
            ),
        ],
        "fatal": decode_bool(elem.attrib.get("fatal", "true"), elem),
    }

check_spelling = partial(
    config_and_apply_text,
    "check_spelling",
    check_spelling_config,
    check_spelling_text,
)

# def include(root: Path, elem: ET.Element) -> Union[List[Union[str, ET.Element]], ET.Element]:
#     assert elem.tag == "include"
#     assert not elem.text
#     assert len(elem) == 0
#     path = root / elem.attrib["path"]
#     itype = elem.attrib.get("type", "str")
#     if itype == "str":
#         return [path.read_text()]
#     elif itype == "xml":
#         return ET.parse(path).getroot()
#     else:
#         raise NotImplementedError(f"Unknown include type {itype}")

def render_code(code: ET.Element) -> ET.Element:
    raise NotImplementedError("See Pygments")

def strip_exif(image: ET.Element) -> ET.Element:
    raise NotImplementedError

def gen_sitemap(site: ET.Element) -> ET.Element:
    # https://en.wikipedia.org/wiki/Robots_exclusion_standard
    # https://en.wikipedia.org/wiki/Site_map
    raise NotImplementedError

def blog_to_pages(blog: ET.Element) -> ET.Element:
    children = []
    assert not blog.attrib
    for i, child in enumerate(blog):
        assert child.tag == "blog_post"
        title = child.find("title")
        assert title is not None
        title_text = title.text
        children.append(
            make_element(
                tag="file",
                attrib=dict(
                    name=f"{i}-{slugify(title_text)}.html",
                ),
                children=[
                    make_element(
                        tag="apply_template",
                        attrib=dict(
                            template="style/blog_post.html.j2",
                            template_lang="jinja",
                            output="xml",
                        ),
                        children=list(child),
                    ),
                ],
            )
        )
    # children.append(
    #     make_element(
    #         tag="file",
    #         attrib=dict(
    #             name="index.html",
    #         ),
    #         children=[
    #             make_element(
    #                 tag="apply_template",
    #                 attrib=dict(
    #                     template="style/blog_index.html.j2",
    #                     template_lang="jinja",
    #                     name="index.html",
    #                     output="xml",
    #                 ),
    #                 text=blog.text,
    #                 tail=blog.tail,
    #                 children=[],
    #             ),
    #         ],
    #     )
    # )
    return children


def write_to_fs(path: Path, elem: ET.Element) -> ET.Element:
    if elem.tag == "file":
        file_path = path / elem.attrib["name"]
        file_path.write_text(inner_to_string(elem))
        return make_element(
            tag=elem.tag,
            attrib=elem.attrib,
            tail=elem.tail,
            children=[],
        )
    elif elem.tag == "dir":
        dir_path = path / elem.attrib["name"]
        dir_path.mkdir()
        return make_element(
            tag=elem.tag,
            attrib=elem.attrib,
            tail=elem.tail,
            text=elem.text,
            children=[write_to_fs(dir_path, child) for child in elem],
        )
    else:
        return make_element(
            tag=elem.tag,
            attrib=elem.attrib,
            tail=elem.tail,
            text=elem.text,
            children=[write_to_fs(path, child) for child in elem],
        )

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("."),
    autoescape=jinja2.select_autoescape(),
)

def apply_template(elem: ET.Element) -> ET.Element:
    templated = {
        "jinja": env.get_template
    }[elem.attrib["template_lang"]](elem.attrib["template"]).render(**{
        child.tag: inner_to_string(child)
            for child in elem
    })
    if elem.attrib["output"] == "xml":
        root = ET.fromstring(templated)
        ElementInclude.include(root)
        return root
    elif elem.attrib["output"] == "string":
        return [templated]
    else:
        raise ValueError(elem.attrib["output"])


dumps = Path("dumps")
if dumps.exists():
    shutil.rmtree(dumps)
dumps.mkdir()
def dump_xml(elem: ET.Element) -> ET.Element:
    i = len(list(dumps.iterdir()))
    path = (dumps / f"{i}.xml")
    assert not path.exists()
    elem = copy.deepcopy(elem)
    ET.indent(elem)
    path.write_bytes(ET.tostring(elem))
    return elem


source = Path("content/site.xml")
output = Path("site")
cwd = Path()

if output.exists():
    shutil.rmtree(output)
output.mkdir()

def strip_whitespace(elem: ET.Element) -> ET.Element:
    text = (elem.text.strip() + (" " if len(elem) != 0 else "")) if elem.text and elem.text.strip() else None
    tail = (" " + elem.tail.strip() + " ") if elem.tail and elem.tail.strip() else None
    return make_element(
        tag=elem.tag,
        attrib=elem.attrib,
        children=[strip_whitespace(child) for child in elem],
        text=text,
        tail=tail,
    )

xml_passes: List[Callable[[ET.Element], ET.Element]] = [
    strip_whitespace,
    smarten_symbols,
    check_spelling,
    check_grammar,
    hyphenate,
    dump_xml,

    # partial(apply_to_tag, "code", render_code),
    # partial(apply_to_tag, "img", strip_exif),

    partial(apply_to_tag, "blog", blog_to_pages),
    partial(apply_to_tag, "apply_template", apply_template),
    strip_whitespace,
    dump_xml,
    # gzip_pages,
    # gen_sitemap,
    partial(apply_to_tag, "fs", partial(write_to_fs, output)),
    dump_xml,
]

root = ET.parse(source).getroot()
ElementInclude.include(root)
for xml_pass in xml_passes:
    root = xml_pass(root)

# TODO: Consistently treat attributes, text, and tail during transformations.
# TODO: Check if site is empty at end.
# TODO: Pass through lang properly.
