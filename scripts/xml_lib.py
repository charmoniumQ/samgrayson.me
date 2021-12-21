from __future__ import annotations
from typing import TypeVar, Callable, Union, List, Mapping, Optional, Dict
import functools
import xml.etree.ElementTree as ET

def make_element(
        tag: str,
        attrib: Dict[str, str] = {},
        text: Optional[str] = None,
        tail: Optional[str] = None,
        children: List[ET.Element] = [],
) -> ET.Element:
    """Constructs an ET.Element."""
    elem = ET.Element(tag, attrib)
    elem.text = text
    elem.tail = tail
    for child in children:
        elem.append(child)
    return elem

def append_string(elem: ET.Element, string: Optional[str]) -> ET.Element:
    if string is None:
        return elem
    children = list(elem)
    if children:
        if children[-1].tail is None:
            children[-1].tail = string
        else:
            children[-1].tail += string
    else:
        if elem.text is None:
            elem.text = string
        else:
            elem.text += string
    return elem

class TagBuilder:
    """Syntactic sugar for constructing an ET.Element.

    Use getattr to name a tag (e.g. `TagBuilder.p`), pass attributes
    as kwargs (optional), and pass children and text as args.

    >>> ET.tostring(TagBuilder.p(
    ...     "hello ",
    ...     TagBuilder.b(style="font-famliy: 10px")("world"),
    ...     "!",
    ... ))
    "<p>hello <b style="font-family: 10px">world</b>!</p>"

    """

    def __getattr__(self, tag: str) -> TagBuilder:
        return functools.partial(self, tag)  # type: ignore

    def __call__(self, tag: str, *children: Union[None, str, ET.Element], **attrib: str) -> Union[TagBuilder, ET.Element]: # type: ignore

        if children:
            ret = make_element(
                tag=tag,
                attrib=attrib,
                text=None,
                tail=None,
                children=[],
            )
            for child in children:
                if child is None:
                    pass
                elif isinstance(child, str):
                    append_string(ret, child)
                elif isinstance(child, ET.Element):
                    ret.append(child)
            return ret
        else:
            return functools.partial(self, tag, **attrib)  # type: ignore

def apply_to_text(func: Callable[[str], str], elem: ET.Element) -> ET.Element:
    """Maps `func` over all the text in `elem`."""
    return make_element(
        tag=elem.tag,
        attrib=elem.attrib,
        text=func(elem.text) if elem.text else None,
        tail=func(elem.tail) if elem.tail else None,
        children=[apply_to_text(func, child) for child in elem],
    )

def apply_to_tag(
        tag: str,
        func: Callable[[ET.Element], Union[ET.Element, List[Union[str, ET.Element]]]],
        elem: ET.Element,
) -> ET.Element:
    """Maps `func` over every occurence of `tag` in `elem`.

    If `func` returns a list, those elements are spliced into the parent.

    If `func` returns a tag, that element replaces the parent."""
    new_elem = _apply_to_tag(tag, func, elem)
    if isinstance(new_elem, ET.Element):
        return new_elem
    elif isinstance(new_elem, list):
        raise ValueError("Root element cannot be splatted into parent.")
    else:
        raise TypeError()

def _apply_to_tag(
        tag: str,
        func: Callable[[ET.Element], Union[ET.Element, List[Union[str, ET.Element]]]],
        elem: ET.Element,
) -> Union[ET.Element, List[Union[str, ET.Element]]]:
    new_elem = make_element(
        tag=elem.tag,
        attrib=elem.attrib,
        text=elem.text,
        tail=elem.tail,
        children=[],
    )
    for child in elem:
        new_child = _apply_to_tag(tag, func, child)
        if isinstance(new_child, list):
            # Splat new_child
            # Append children of new_child into parent
            for new_child2 in new_child:
                if isinstance(new_child2, ET.Element):
                    new_elem.append(new_child2)
                elif isinstance(new_child2, str):
                    append_string(new_elem, new_child2)
                else:
                    raise TypeError()
        elif isinstance(new_child, ET.Element):
            new_elem.append(new_child)
        else:
            raise TypeError()
    if elem.tag == tag:
        return func(new_elem)
    else:
        return new_elem

def expand_splat(elem: ET.Element) -> ET.Element:
    """Expands elements whose tag is `splat_tag` into their parent.

    >>> ET.tostring(expand_splat(ET.fromstring('''
    <head>
      <*>
        <script>1</script>
      </*>
      <script>2</script>
    </head>
    ''')))
    <head>
      <script>1</script>
      <script>2</script>
    </head>

    This is like a splice in Lisp.
    """
    ret = make_element(
        tag=elem.tag,
        attrib=elem.attrib,
        text=elem.text,
        tail=elem.tail,
        children=[]
    )
    for child in elem:
        if child.tag == "*":
            assert not child.attrib
            append_string(ret, child.text)
            ret.extend(expand_splat(child))
            append_string(ret, child.tail)
        else:
            ret.append(expand_splat(child))
    return ret

def inner_to_string(elem: ET.Element, **kwargs: Any) -> str:
    """
    >>> inner_text(ET.fromstring("<a>abc<b>def</b>ghi</a>")) == "abc<b>def</b>ghi"
    """
    ibuffer = elem.text if elem.text else ""
    for child in elem:
        ibuffer += ET.tostring(child, **kwargs).decode()
        if child.tail:
            ibuffer += child.tail
    return ibuffer

def inner_text(elem: ET.Element) -> str:
    """
    >>> inner_text(ET.fromstring("<a>abc<b>def</b>ghi</a>")) == "abcdefghi"
    """
    ibuffer = ""
    if elem.text:
        ibuffer += elem.text
    for child in elem:
        ibuffer += inner_text(child)
        if child.tail:
            ibuffer += child.tail
    return ibuffer
