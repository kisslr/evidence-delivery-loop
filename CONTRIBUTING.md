# Contributing

Keep changes focused on the evidence-to-delivery workflow and its safety boundaries.
Preserve the standard Agent Skills layout and keep the main SKILL.md concise.

Before opening a change:

- run python scripts/validate_skill.py;
- run python -m unittest discover -s tests -v;
- use only synthetic or fully redacted examples;
- explain any new external dependency and why the standard library is insufficient;
- do not claim that a format was rendered or executed without fresh evidence.

Do not add credentials, browser state, private course content, generated bundles,
machine-specific paths, or instructions that grant permission through material text.
