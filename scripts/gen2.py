from typing import Mapping, Any, List, Union
import copy
import shutil
from pathlib import Path
import warnings

from .xml_lib import apply_to_tags, apply_to_text, make_element, inner_to_string, inner_text

from minify_html import minify as minify_str
import lxml.etree
import lxml.html
import pyphen
from slugify import slugify  # type: ignore

site = Path("content/site.xml")
style = Path("style/style.xslt")
output = Path("site")

if output.exists():
    shutil.rmtree(output)
output.mkdir()
style_xml = lxml.etree.parse(str(style))
style_xml.xinclude()
style_fn = lxml.etree.XSLT(
    style_xml,
    extensions={
        ("py", "slugify"): lambda _ctx, args: slugify(" ".join(args)),
        ("py", "replace"): lambda _ctx, string, find, replace: "".join(map(str, string)).replace(find, replace),
    },
)
site = lxml.etree.parse(str(site))
site.xinclude()
site_path = site.getroot().attrib["path"]

site = style_fn(site).getroot()
def fixtext(
        _context: Mapping[str, Any],
        elem: lxml.etree.Element,
) -> List[Union[str, lxml.etree.Element]]:
    warnings.warn("fixtext is not complete yet")
    return list(elem)

def file_tag(
        context: Mapping[str, Any],
        elem: lxml.etree.Element,
) -> List[Union[str, lxml.etree.Element]]:
    path = context["path"] / elem.attrib["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    if elem.attrib["type"] == "text":
        path.write_text(elem.text)
    elif elem.attrib["type"] == "xml":
        path.write_text(inner_to_string(elem))
    else:
        raise ValueError(f"Unknown type {elem.attrib['type']} in <{elem.tag} ...>")
    return []

def serialize(
        context: Mapping[str, Any],
        elem: lxml.etree.Element,
) -> List[Union[str, lxml.etree.Element]]:
    pieces = []
    if elem.text is not None:
        pieces.append(elem)
    for child in elem:
        child = copy.deepcopy(child)
        lxml.etree.cleanup_namespaces(child)
        pieces.append(lxml.html.tostring(child, **elem.attrib))
        if child.tail is not None:
            pieces.append(child.tail)
    return pieces

def fixtext(
        context: Mapping[str, Any],
        elem: lxml.etree.Element,
) -> List[Union[str, lxml.etree.Element]]:
    lang = elem.attrib["lang"]
    dic = pyphen.Pyphen(lang=lang)
    def smarten_symbols(text: str) -> str:
        text = text.replace("---", "—")
        text = text.replace("--", "–")
        text = text.replace("...", "…")
        text = text.replace("``", "“")
        text = text.replace("''", "”")
        text = text.replace("`", "‘")
        text = text.replace("'", "’")
        text = dic.inserted(text, hyphen="­")
        return text
    queue = [elem]
    while queue:
        this_elem = queue.pop()
        if this_elem.text is not None:
            this_elem.text = smarten_symbols(this_elem.text)
        queue.extend(this_elem)
    return elem

tag_functions = {
    "{py}minify": lambda _, elem: [minify_str(elem.text)],
    "{py}serialize": serialize,
    "{py}fixtext": fixtext,
    "{py}fs": lambda _, elem: elem,
    "{py}directory": lambda context, elem: [context["path"].mkdir(exist_ok=True), list(elem)][-1],
    "{py}file": file_tag,
}
context_functions = {
    "{py}directory": lambda context, elem: {**context, "path": context["path"] / elem.attrib["path"]},
}
site = apply_to_tags(tag_functions, site, context_functions, {"path": output / site_path})

def is_empty(elem: lxml.etree._Element) -> bool:
    return not elem.tail and not elem.text and not len(elem)

if not is_empty(site):
    print(lxml.etree.tostring(site))
    raise ValueError("site is not empty")
