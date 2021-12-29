from typing import Mapping, Any, List, Union
import copy
import datetime
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
output = Path("docs/")

def raise_(exc: Exception) -> None:
    raise exc

if output.exists():
    shutil.rmtree(output)
output.mkdir()
style_xml = lxml.etree.parse(str(style))
style_xml.xinclude()
style_xml.xinclude()
style_fn = lxml.etree.XSLT(
    style_xml,
    extensions={
        ("py", "slugify"): lambda _ctx, args: slugify(" ".join(args)),
        ("py", "replace"): lambda _ctx, string, find, replace: "".join(map(str, string)).replace(find, replace),
        ("py", "error"): lambda _ctx: raise_(RuntimeError()),
        ("py", "join"): lambda _ctx, *args: "/".join(
            "".join(arg) for arg in args
        ),
    },
)
site = lxml.etree.parse(str(site))
site.xinclude()
site = site.getroot()
def set_vocabulary(ctx, elem):
    for child in elem:
        ctx["vocabulary"][child.attrib["id"]] = child
    return []
def ref_vocabulary(ctx, elem):
    ref = ctx["vocabulary"][elem.attrib["ref"]]
    if elem.attrib.get("splat", False):
        return list(ref)
    else:
        return ref

site = apply_to_tags(
    tag_funcs={
        "set-vocabulary": lambda _ctx, _elem: [],
        "ref-vocabulary": ref_vocabulary,
    },
    elem=site,
    context_funcs={
        "set-vocabulary": set_vocabulary,
    },
    context={
        "vocabulary": {}
    },
)
site_path = site.attrib["path"]

site = style_fn(site)
site = site.getroot()

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
    lang = elem.attrib["lang"].replace("-", "_")
    hyphen_dict = pyphen.Pyphen(lang=lang)
    def smarten_symbols(text: str) -> str:
        text = text.replace("---", "—")
        text = text.replace("--", "–")
        text = text.replace("...", "…")
        text = text.replace("``", "“")
        text = text.replace("''", "”")
        text = text.replace("`", "‘")
        text = text.replace("'", "’")
        text = hyphen_dict.inserted(text, hyphen="­")
        return text
    queue = [elem]
    while queue:
        this_elem = queue.pop()
        if this_elem.text is not None:
            this_elem.text = smarten_symbols(this_elem.text)
        queue.extend(this_elem)
    # TODO: spellcheck
    # TODO: grammar check
    return list(elem)

minify_config = {
    "do_not_minify_doctype": True,
    "ensure_spec_compliant_unquoted_attribute_values": True,
    "keep_closing_tags": True,
    "keep_html_and_head_opening_tags": True,
    "keep_spaces_between_attributes": True,
    "keep_comments": False,
    "minify_css": True,
    "minify_js": True,
    "remove_bangs": True,
    "remove_processing_instructions": True,
}

tag_functions = {
    "{py}minify": lambda _, elem: [minify_str(elem.text, **minify_config)],
    "{py}serialize": serialize,
    "{py}fixtext": fixtext,
    "{py}fs": lambda _, elem: elem,
    "{py}directory": lambda context, elem: [context["path"].mkdir(exist_ok=True), list(elem)][-1],
    "{py}file": file_tag,
    "{py}warn": lambda _, elem: [warnings.warn(elem.text), []][-1],
    "{py}date": lambda _, datestr: [datetime.datetime.fromisoformat(datestr.text).strftime("%B %d, %Y")],
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
