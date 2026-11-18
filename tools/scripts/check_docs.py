# ===== AI GENERATED: check_documentation =====
# Purpose: Check repository Markdown links, heading anchors and fenced blocks.
# Inputs: Markdown files in docs plus the project and application READMEs.
# Returns: A nonzero exit code and actionable messages when references break.
# Flow: Discover pages, resolve local links, validate anchors and report failures.

"""Run from any directory: python tools/scripts/check_docs.py."""

import re
import unicodedata
from pathlib import Path
from urllib.parse import unquote

WORKSPACE = Path(__file__).resolve().parents[2]
FENCE = re.compile(r"^\s*(`{3,}|~{3,})", re.MULTILINE)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def heading_anchors(content: str) -> set[str]:
    """Return GitHub-style anchors, including suffixes for repeated headings."""
    content = re.sub(r"```.*?```|~~~.*?~~~", "", content, flags=re.DOTALL)
    occurrences: dict[str, int] = {}
    anchors: set[str] = set()
    for heading in re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE):
        heading = re.sub(r"<[^>]+>", "", heading).strip().lower()
        anchor = "".join(
            character
            for character in heading
            if character in "-_ " or unicodedata.category(character)[0] in "LN"
        ).replace(" ", "-")
        occurrence = occurrences.get(anchor, 0)
        occurrences[anchor] = occurrence + 1
        anchors.add(f"{anchor}-{occurrence}" if occurrence else anchor)
    return anchors


def check_documentation() -> int:
    """Check tracked documentation locations without reading secrets or dependencies."""
    documents = sorted((WORKSPACE / "docs").rglob("*.md"))
    documents.extend(
        WORKSPACE / relative_path
        for relative_path in (
            "README.md",
            "src/frontend/README.md",
            "tools/README.md",
            ".github/file-structure.md",
        )
    )
    failures: list[str] = []
    link_count = 0
    for document in documents:
        content = document.read_text(encoding="utf-8")
        label = document.relative_to(WORKSPACE).as_posix()
        if len(FENCE.findall(content)) % 2:
            failures.append(f"{label}: unbalanced code fences")
        if content.count("<details>") != content.count("</details>"):
            failures.append(f"{label}: unbalanced detail disclosures")
        content = re.sub(r"```.*?```|~~~.*?~~~", "", content, flags=re.DOTALL)
        for reference in LINK.findall(content):
            if re.match(r"[a-z][a-z0-9+.-]*:", reference, re.IGNORECASE):
                continue
            filename, _, fragment = unquote(reference.strip("<>")).partition("#")
            target = (document.parent / filename).resolve() if filename else document
            link_count += 1
            if not target.exists():
                failures.append(f"{label}: missing {reference}")
            elif fragment and target.suffix == ".md":
                if fragment not in heading_anchors(target.read_text(encoding="utf-8")):
                    failures.append(f"{label}: missing anchor {reference}")
    print(f"Checked {len(documents)} Markdown pages and {link_count} local links/anchors.")
    for failure in failures:
        print(failure)
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(check_documentation())
