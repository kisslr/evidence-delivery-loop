"""Dependency-free structural and safety checks for the repository skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

MAX_DESCRIPTION_LENGTH = 1024
MAX_BODY_LINES = 500
ALLOWED_FRONTMATTER = {"name", "description"}
REQUIRED_SECTIONS = (
    "## Operating contract",
    "## Activation and intake",
    "## Workflow",
    "## Skill coordination",
    "## Default response contract",
)
REQUIRED_FILES = (
    "README.md",
    "README_EN.md",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    ".gitignore",
    ".gitattributes",
    ".github/workflows/validate.yml",
    "skills/evidence-delivery-loop/SKILL.md",
    "skills/evidence-delivery-loop/agents/openai.yaml",
    "skills/evidence-delivery-loop/references/format-routing.md",
    "skills/evidence-delivery-loop/references/safety-matrix.md",
    "skills/evidence-delivery-loop/references/output-contract.md",
)
SENSITIVE_PATTERNS = (
    re.compile(r"(?i)\b(?:ghp|github_pat)_[a-z0-9_]+"),
    re.compile(r"(?i)\bsk-[a-z0-9]{20,}"),
    re.compile(r"(?i)\bBearer\s+[a-z0-9._-]{12,}"),
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(?:session|auth|csrf)[_-]?(?:cookie|token)\s*[:=]\s*\S+"),
    re.compile(r"(?i)[A-Z]:\\Users\\[a-zA-Z0-9._-]+|[A-Z]:\\Development\\Projects"),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(content: str) -> dict[str, str]:
    """Parse the deliberately small JSON-quoted frontmatter subset we publish."""
    lines = content.splitlines()
    if len(lines) < 3 or lines[0] != "---":
        raise ValueError("frontmatter must start with ---")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("frontmatter closing delimiter is missing") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):[ \t]*(.*)", line)
        if not match:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, raw = match.groups()
        if key in values:
            raise ValueError(f"duplicate frontmatter key: {key}")
        if key not in ALLOWED_FRONTMATTER:
            raise ValueError(f"unexpected frontmatter key: {key}")
        if raw.startswith('"'):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid quoted value for {key}") from exc
        else:
            value = raw.strip()
        if not isinstance(value, str):
            raise ValueError(f"frontmatter value for {key} must be a string")
        values[key] = value
    missing = ALLOWED_FRONTMATTER - values.keys()
    if missing:
        raise ValueError(f"missing frontmatter key(s): {', '.join(sorted(missing))}")
    return values


def scan_text(text: str) -> list[str]:
    """Return names of sensitive patterns without echoing matched material."""
    return [str(index) for index, pattern in enumerate(SENSITIVE_PATTERNS) if pattern.search(text)]


def validate_frontmatter(content: str) -> list[str]:
    errors: list[str] = []
    try:
        values = parse_frontmatter(content)
    except ValueError as exc:
        return [str(exc)]
    name = values["name"]
    if (
        not re.fullmatch(r"[a-z0-9-]{1,64}", name)
        or name.startswith("-")
        or name.endswith("-")
        or "--" in name
    ):
        errors.append("skill name is not valid hyphen-case")
    description = values["description"]
    if not description:
        errors.append("skill description must not be empty")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append("skill description exceeds 1024 characters")
    if "<" in description or ">" in description:
        errors.append("skill description cannot contain angle brackets")
    return errors


def _validate_openai_yaml(path: Path) -> list[str]:
    errors: list[str] = []
    text = _read(path)
    if "\t" in text:
        errors.append("agents/openai.yaml contains tabs")
    required = (
        "interface:",
        '  display_name: "',
        '  short_description: "',
        '  default_prompt: "',
        "policy:",
        "  allow_implicit_invocation: true",
    )
    for marker in required:
        if marker not in text:
            errors.append(f"agents/openai.yaml missing required marker: {marker}")
    values: dict[str, str] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        match = re.search(rf"(?m)^  {key}: (\".*\")$", text)
        if not match:
            errors.append(f"agents/openai.yaml has an invalid {key} value")
            continue
        try:
            values[key] = json.loads(match.group(1))
        except json.JSONDecodeError:
            errors.append(f"agents/openai.yaml has an invalid quoted {key} value")
    short_description = values.get("short_description", "")
    if short_description and not 25 <= len(short_description) <= 64:
        errors.append("agents/openai.yaml short_description must be 25-64 characters")
    if values.get("default_prompt") and "$evidence-delivery-loop" not in values["default_prompt"]:
        errors.append("agents/openai.yaml default_prompt must mention the skill")
    return errors


def validate_repo(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = root / "skills/evidence-delivery-loop/SKILL.md"
    if skill_path.is_file():
        content = _read(skill_path)
        errors.extend(validate_frontmatter(content))
        if len(content.splitlines()) > MAX_BODY_LINES:
            errors.append("SKILL.md exceeds 500 lines")
        if "[TODO" in content or "PLACEHOLDER" in content:
            errors.append("SKILL.md still contains template placeholders")
        for section in REQUIRED_SECTIONS:
            if section not in content:
                errors.append(f"SKILL.md missing section: {section}")

    metadata_path = root / "skills/evidence-delivery-loop/agents/openai.yaml"
    if metadata_path.is_file():
        errors.extend(_validate_openai_yaml(metadata_path))

    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.stat().st_size > 2_000_000:
            errors.append(f"unexpectedly large text candidate: {path.relative_to(root)}")
            continue
        try:
            text = _read(path)
        except UnicodeDecodeError:
            continue
        if scan_text(text):
            errors.append(f"sensitive pattern found in: {path.relative_to(root)}")
    return errors


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)
    errors = validate_repo(Path(args.root))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    print("Validation passed: repository structure, metadata, safeguards, and sensitive-data scan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
