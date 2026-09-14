"""Dependency-free structural, safety, and release-contract checks for the skill."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable

MAX_DESCRIPTION_LENGTH = 240
MAX_SKILL_WORDS = 1100
MAX_BODY_LINES = 220
ALLOWED_FRONTMATTER = {"name", "description"}
REQUIRED_SECTIONS = (
    "## Operating contract",
    "## Activation and intake",
    "## Workflow",
    "## Skill coordination",
    "## Default response contract",
)
REQUIRED_REFERENCE_LINKS = (
    "references/safety-matrix.md",
    "references/format-routing.md",
    "references/output-contract.md",
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
    "evaluations/forward-eval.md",
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
MARKDOWN_LINK = re.compile(r"\[[^\]\n]+\]\(([^)\s]+)\)")
WORD_PATTERN = re.compile(r"\b[\w'-]+\b")
ARCHIVE_POLICY_MARKERS = (
    "500 members",
    "250 mib",
    "50:1",
    "aggregate across all nested archives",
    "must not reset per inner archive",
)
WEB_PREFLIGHT_PATTERN = re.compile(
    r"classification-only preflight.*?response headers with no response body"
)
WEB_BODY_GATE_PATTERN = re.compile(
    r"only a final response with a textual media type.*?"
    r"ambiguous classification is s3 before any body retrieval"
)
ARCHIVE_RESET_PERMISSION_PATTERN = re.compile(
    r"\b(?:each|every)\s+(?:inner|nested)\s+archive\s+"
    r"(?:may|can|is allowed to)\s+reset\s+(?:its|the)?\s*"
    r"(?:budget|limit|counter)\b"
)
S0_BODY_BEFORE_CLASSIFICATION_PATTERN = re.compile(
    r"\bs0\s+(?:may|can|is allowed to)\s+"
    r"(?:read|fetch|retrieve)\s+(?:a|the)?\s*"
    r"(?:response|page)?\s*body\s+before\s+classification\b"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _body_after_frontmatter(content: str) -> str:
    lines = content.splitlines()
    try:
        end = lines.index("---", 1)
    except ValueError:
        return content
    return "\n".join(lines[end + 1 :])


def _markdown_targets(content: str) -> set[str]:
    return {match.group(1) for match in MARKDOWN_LINK.finditer(content)}


def _normalize_contract_text(content: str) -> str:
    return " ".join(content.lower().split())


def _validate_policy_contract(safety_text: str, routing_text: str) -> list[str]:
    errors: list[str] = []
    normalized_safety = _normalize_contract_text(safety_text)
    normalized_routing = _normalize_contract_text(routing_text)
    for label, content in (
        ("safety-matrix", normalized_safety),
        ("format-routing", normalized_routing),
    ):
        if not all(marker in content for marker in ARCHIVE_POLICY_MARKERS):
            errors.append(f"{label} archive policy is incomplete")
        if ARCHIVE_RESET_PERMISSION_PATTERN.search(content):
            errors.append(f"{label} archive policy contains a reset permission")
    if not (
        WEB_PREFLIGHT_PATTERN.search(normalized_safety)
        and WEB_BODY_GATE_PATTERN.search(normalized_safety)
    ):
        errors.append("safety-matrix web classification gate is incomplete")
    if S0_BODY_BEFORE_CLASSIFICATION_PATTERN.search(normalized_safety):
        errors.append("safety-matrix allows S0 body retrieval before classification")
    return errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    """Return sensitive-pattern indexes without echoing matched material."""
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
        errors.append("skill description exceeds 240 characters")
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


def _skill_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file()
    }


def compare_skill_trees(source_dir: Path, installed_dir: Path) -> list[str]:
    """Compare release files by relative path and SHA-256 without exposing contents."""
    source_dir = source_dir.resolve()
    installed_dir = installed_dir.resolve()
    if not source_dir.is_dir():
        return ["source skill directory is missing"]
    if not installed_dir.is_dir():
        return ["installed skill directory is missing"]
    try:
        same_location = source_dir.samefile(installed_dir)
    except OSError:
        same_location = source_dir == installed_dir
    if same_location:
        return ["installed skill directory must differ from source skill directory"]

    source_files = _skill_files(source_dir)
    installed_files = _skill_files(installed_dir)
    errors: list[str] = []

    for relative in sorted(source_files.keys() - installed_files.keys()):
        errors.append(f"missing installed file: {relative}")
    for relative in sorted(installed_files.keys() - source_files.keys()):
        errors.append(f"unexpected installed file: {relative}")
    for relative in sorted(source_files.keys() & installed_files.keys()):
        if _sha256(source_files[relative]) != _sha256(installed_files[relative]):
            errors.append(f"content differs: {relative}")
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
        body = _body_after_frontmatter(content)
        errors.extend(validate_frontmatter(content))
        if len(body.splitlines()) > MAX_BODY_LINES:
            errors.append("SKILL.md exceeds 220 lines")
        if len(WORD_PATTERN.findall(body)) > MAX_SKILL_WORDS:
            errors.append("SKILL.md exceeds 1100 words")
        if "[TODO" in content or "PLACEHOLDER" in content:
            errors.append("SKILL.md still contains template placeholders")
        for section in REQUIRED_SECTIONS:
            if section not in content:
                errors.append(f"SKILL.md missing section: {section}")
        targets = _markdown_targets(content)
        for relative in REQUIRED_REFERENCE_LINKS:
            if relative not in targets:
                errors.append(f"SKILL.md missing conditional reference link: {relative}")

    metadata_path = root / "skills/evidence-delivery-loop/agents/openai.yaml"
    if metadata_path.is_file():
        errors.extend(_validate_openai_yaml(metadata_path))

    safety_path = root / "skills/evidence-delivery-loop/references/safety-matrix.md"
    routing_path = root / "skills/evidence-delivery-loop/references/format-routing.md"
    if safety_path.is_file() and routing_path.is_file():
        errors.extend(_validate_policy_contract(_read(safety_path), _read(routing_path)))

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
    parser.add_argument(
        "--installed-skill",
        type=Path,
        help="compare the repository skill with an installed deployment directory",
    )
    args = parser.parse_args(argv)
    root = Path(args.root)
    errors = validate_repo(root)
    if args.installed_skill is not None:
        errors.extend(
            compare_skill_trees(root / "skills/evidence-delivery-loop", args.installed_skill)
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    if args.installed_skill is None:
        print("Validation passed: repository structure, safeguards, and sensitive-data scan.")
    else:
        print("Validation passed: repository structure, safeguards, sensitive-data scan, and release contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
