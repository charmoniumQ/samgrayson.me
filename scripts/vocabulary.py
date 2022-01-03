from typing import Mapping, Any
import copy
import lxml.etree as ET
from .xml_lib import apply_to_tags, ignore_tag_func

def set_vocabulary(ctx: Mapping[str, Any], elem: ET._Element):
    ctx = copy.deepcopy(ctx)
    for child in elem:
        ctx["vocabulary"][child.attrib["id"]] = child
    return ctx

def ref_vocabulary(ctx: Mapping[str, Any], elem: ET._Element):
    ref = ctx["vocabulary"][elem.attrib["ref"]]
    if elem.attrib.get("splat", False):
        return list(ref)
    else:
        return ref

def apply_vocabulary(elem: ET._Element, default_vocabulary: Mapping[str, str] = {}) -> ET._Element:
    return apply_to_tags(
        tag_funcs={
            "set-vocabulary": ignore_tag_func,
            "ref-vocabulary": ref_vocabulary,
        },
        elem=elem,
        context_funcs={
            "set-vocabulary": set_vocabulary,
        },
        context={
            "vocabulary": default_vocabulary,
        },
    )
