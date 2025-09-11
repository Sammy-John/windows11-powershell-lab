from __future__ import annotations
import re
from pathlib import Path
import mkdocs_gen_files

# Configure the sections you want auto-indexed.
# key = folder under docs/, value = (Human Title, intro blurb)
SECTIONS = {
    "guides": (
        "📝 Guides",
        "Step-by-step install and configuration walkthroughs for Windows tools, features, and security tasks. "
    ),
    "notes": (
        "📒 Notes",
        "Focused learning notes for Windows 11 features and tools. "
    ),
    "powershell": (
        "⚡ PowerShell",
        "Hands-on learning notes covering core concepts, commands, and administration tasks. "
    ),
    "scripts": (
        "📦 Scripts",
        "Example scripts you can adapt and run in your own environments. "
    ),
    "cheatsheet": (
        "🧠 Cheatsheet",
        "Quick syntax and examples for faster work. "
    ),
}

DOCS_DIR = Path("docs")
IGNORE_BASENAMES = {"index.md", "README.md", ".pages"}
TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)

def extract_title(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8", errors="ignore")

    # Front matter "title:" (lightweight parse)
    if text.startswith(("---\n", "---\r\n")):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            for line in fm.splitlines():
                if line.strip().lower().startswith("title:"):
                    return line.split(":", 1)[1].strip().strip('"\'')
    # First H1
    m = TITLE_RE.search(text)
    if m:
        return m.group(1).strip()

    return md_path.stem.replace("-", " ").title()

def _gather_items(section_dir: Path):
    items = []
    if not section_dir.exists():
        return items
    for p in section_dir.rglob("*.md"):
        if p.name in IGNORE_BASENAMES:
            continue
        rel = p.relative_to(section_dir)
        # Pretty URL: strip .md, add trailing slash; normalize for Windows
        url = str(rel.with_suffix("")).replace("\\", "/") + "/"
        title = extract_title(p)
        items.append((title, url))
    # Sort by title; change to reverse mtime if you prefer "latest first"
    items.sort(key=lambda x: x[0].lower())
    return items

def _render_index_md(title: str, intro: str, items: list[tuple[str, str]]) -> str:
    out = []
    out.append(f"# {title}\n")
    out.append(intro + "\n")
    out.append("## Contents\n")
    if not items:
        out.append("- _Nothing here yet — add some `.md` files to this section._\n")
    else:
        for t, url in items:
            out.append(f"- **[{t}]({url})**")
    out.append("")  # trailing newline
    return "\n".join(out)

# ... all your functions above ...

def build_all_indexes(**_kwargs):
    for folder, (human_title, intro) in SECTIONS.items():
        section_dir = DOCS_DIR / folder
        items = _gather_items(section_dir)
        content = _render_index_md(human_title, intro, items)
        with mkdocs_gen_files.open(f"{folder}/index.md", "w") as f:
            f.write(content)

# IMPORTANT: run it when mkdocs executes this script
build_all_indexes()

