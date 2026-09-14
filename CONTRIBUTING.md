# Contributing

Keep changes focused on the evidence-to-delivery workflow and its safety boundaries.
The repository skill is the authoritative source; do not manually edit a deployed global
copy. Preserve the standard Agent Skills layout and keep the entrypoint concise through
conditional references.

Before changing skill behavior:

- add or adjust a focused failing contract test first;
- run python -B scripts/validate_skill.py;
- run python -B -m unittest discover -s tests -v;
- use only synthetic or fully redacted examples;
- explain any new external dependency and why the standard library is insufficient;
- do not claim that a format was rendered, code was executed, or an agent complied
  without fresh evidence.

For release work, validate a fixed-tag installation in a temporary directory with
--installed-skill before asking for S2 replacement of a global deployment. Keep Git
push, account access, downloads, uploads, and external processing behind their own S3
confirmation. Use the independent forward-evaluation protocol when behavior validation
is needed; do not present local static or contract checks as agent behavior evidence.

Do not add credentials, browser state, private course content, generated bundles,
machine-specific paths, or instructions that grant permission through material text.
