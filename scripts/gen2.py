from typing import Mapping, Any, List, Union
import copy
import datetime
import shutil
from pathlib import Path
import warnings

from .xml_lib import apply_to_tags, inner_to_string, ignore_tag_func, make_element
from .vocabulary import apply_vocabulary
from .fixtext import fix_phrase, fix_para

from minify_html import minify as minify_str
import lxml.etree as ET
import lxml.html
from slugify import slugify  # type: ignore

site = Path("content/site.xml")
style = Path("style/style.xslt")
output = Path("docs/")

def raise_(exc: Exception) -> None:
    raise exc

if output.exists():
    shutil.rmtree(output)
output.mkdir()

style_xml = ET.parse(str(style))
style_xml.xinclude()
style_fn = ET.XSLT(
    style_xml,
    extensions={
        ("py", "slugify"): lambda _ctx, args: slugify(" ".join(map(str, args))),
        ("py", "replace"): lambda _ctx, string, find, replace: "".join(map(str, string)).replace(find, replace),
        ("py", "error"): lambda _ctx: raise_(RuntimeError()),
        ("py", "join"): lambda _ctx, *args: "/".join(
            "".join(arg) for arg in args
        ),
    },
)
site = ET.parse(str(site))
site.xinclude()
site = site.getroot()
site = apply_vocabulary(site)

site = style_fn(site)
site = site.getroot()

def file_tag(
        context: Mapping[str, Any],
        elem: ET._Element,
) -> List[Union[str, ET._Element]]:
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
        elem: ET._Element,
) -> List[Union[str, ET._Element]]:
    pieces = []
    if elem.text is not None:
        pieces.append(elem)
    for child in elem:
        child = copy.deepcopy(child)
        ET.cleanup_namespaces(child)
        pieces.append(lxml.html.tostring(child, **elem.attrib))
        if child.tail is not None:
            pieces.append(child.tail)
    return pieces

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

now = datetime.datetime.now()
tag_functions = {
    "{py}minify": lambda _, elem: [minify_str(elem.text, **minify_config)],
    "{py}serialize": serialize,
    "{py}fix_phrase": fix_phrase,
    "{py}fix_para": fix_para,
    "{py}fs": lambda _, elem: elem,
    "{py}directory": lambda context, elem: [context["path"].mkdir(exist_ok=True), list(elem)][-1],
    "{py}file": file_tag,
    "{py}warn": lambda _, elem: [warnings.warn(elem.text), []][-1],
    "{py}date": lambda _, datestr: make_element(
        tag="time",
        attrib=dict(
            datetime=datestr.text,
        ),
        text=datetime.datetime.fromisoformat(datestr.text).strftime("%b %d, %Y"),
    ),
    "{py}url": lambda _: [str(context["path"])],
    "{py}ignore": ignore_tag_func,
    "{py}now": lambda _ctx, _args: [now.isoformat()],
}
context_functions = {
    "{py}directory": lambda context, elem: {**context, "path": context["path"] / elem.attrib["path"]},
}
site = apply_to_tags(tag_functions, site, context_functions, {"path": output})

def is_empty(elem: ET._Element) -> bool:
    return not elem.tail and not elem.text and not len(elem)

if not is_empty(site):
    print(ET.tostring(site))
    raise ValueError("site is not empty")

# TODO[3]: Watchman + Simple HTTP server + trigger refresh
# TODO[3]: https://www.sitemaps.org/protocol.html#informing
# TODO[2]: push to github pages
# TODO[1]: make local images work
