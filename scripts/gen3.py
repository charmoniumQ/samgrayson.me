import shutil
import subprocess
import yaml
from yamlinclude import YamlIncludeConstructor
from pathlib import Path
from typing import TypeVar, Dict

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

YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader, base_dir=content.parent)

content = Path("content/site.yaml")
output = Path("build")
if output.exists():
    shutil.rmdir(output)
output.mkdir()

site = yaml.load(
    (content.parent / "site.yaml").read_text(),
    Loader=yaml.FullLoader,
)

(output / "blog").mkdir()
for post in site["blog"]["content"]:
    content = run_pandoc(content.parent / Path(post["content"]["pandoc_file"]))
    (output / "blog" / post["slug"]).with_suffix("html").write_text(content)

print(site)