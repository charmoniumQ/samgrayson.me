import re
import io
import datetime
import xml.etree.ElementTree as ETree
import jinja2
import shutil
import subprocess
import yaml
from yamlinclude import YamlIncludeConstructor
from pathlib import Path
from typing import TypeVar, Dict
import xml_lib

def run_pandoc(pandoc_file: Path) -> str:
    return subprocess.run(
        ["pandoc", "--to", "html4", str(pandoc_file)],
        text=True,
        capture_output=True,
    ).stdout

K = TypeVar("K")
V = TypeVar("V")
def assign(dct: Dict[K, V], key: K, value: V) -> Dict[K, V]:
    dct[key] = value
    return dct

site_file = Path("content/site.yaml")

YamlIncludeConstructor.add_to_loader_class(
    loader_class=yaml.FullLoader,
    base_dir=site_file.parent,
)
site = yaml.load(
    site_file.read_text(),
    Loader=yaml.FullLoader,
)
site["root"] = site_file.parent

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(site["root"]),
    autoescape=True,
)
jinja_env.filters["html2text"] = lambda html: re.sub(r"<[^>]*>", "", html)
jinja_env.filters["iso_date"] = lambda date: date.toisoformat()
jinja_env.filters["human_readable_date"] = lambda date: date.strftime("%Y %B %d")

page_template = jinja_env.get_template(site["template"])
output = Path("docs")
if output.exists():
    shutil.rmtree(output)
output.mkdir()

for section in site["sections"]:
    (output / section["slug"]).mkdir()
    section_template = jinja_env.get_template(section["template"])
    for post in section["content"]:
        url = site["url"] + "/" + section["slug"] + "/" + post["slug"] + ".html"
        post = {
            "url": url,
            "content": run_pandoc(site["root"] / Path(post["content"]["pandoc_file"])),
            **post,
        }
        (output / section["slug"] / post["slug"]).with_suffix(".html").write_text(
            page_template.render(**{
                "page": {
                    **post,
                    "content": section_template.render(post=post),
                },
                "site": site,
            })
        )

# TODO[1]: Test that title is less than 70 and teaser is less than 200 characters
