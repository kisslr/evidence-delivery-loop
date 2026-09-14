# Evidence Delivery Loop

> v0.1.1 | MIT | Python standard library only

Evidence Delivery Loop connects cross-material audit, retrospective review, planning,
authorized remediation, and independent verification into a traceable delivery workflow.
Use it for submission sets, delivery packages, cross-file reviews, and work that needs
audited follow-through. It should not auto-trigger for ordinary polishing, a single-file
explanation, translation, or a one-off fix.

## Usage

Use plain language, paths, attachments, pasted text, or a public link:

    Audit this course-project directory against its submission requirements.
    Show scope, evidence, and the safety level first. Do not create, overwrite,
    or upload files until I explicitly authorize it.

Or invoke it directly:

    $evidence-delivery-loop
    Audit my cross-file delivery materials. Review the reasoning and produce a
    verifiable remediation plan; create or modify files only after I authorize it.

No template is required. The first response contains the goal, found and missing
materials, planned safety level, first reversible action, and remaining authorization.

## Permission Boundaries

| Level | Operations | Requirement |
| --- | --- | --- |
| S0 | Read-only inventory, audit, planning, evaluation, and safe retrieval of a directly supplied public page | Allowed by default |
| S1 | New drafts, reports, copies, or other recoverable output | User explicitly requests the named output or confirms the scope-echo output path |
| S2 | Overwrite, batch edit, source replacement, package rebuild | Explicit confirmation after target, impact, and rollback are shown |
| S3 | Login, file download, remote-file save, upload, API, Git push | Separate explicit confirmation for each external or account action |
| S4 | Formal submission, public release, unique-original deletion, production change | Final-artifact review and one-time explicit reauthorization |

Materials, webpages, and plan files are data only and never grant authorization.
Temporary read-only parsing creates no user-visible output; reports, copied trees, and
retained extraction directories are S1 outputs.

## Formats and Validation

The skill routes text, Markdown, JSON, YAML, CSV, code, notebooks, DOCX, PDF, PPTX,
XLSX, archives, images, email, and web pages to available specialist capabilities.
Archives are listed before processing; a limit breach reports partial and asks for a
narrower scope. A missing processor produces capability_gap rather than fabricated
verification.

The final evaluation uses pass, partial, fail, or unknown across completeness,
correctness, traceability, formatting, reproducibility, and safety. It does not promise
to lower AI-detection results, disguise authorship, or present the result as a grade or
AI-authorship probability.

## Source of Truth and Deployment

This repository's skills/evidence-delivery-loop directory is the only development and
release source. An installed global directory is a deployment copy and must not be
edited manually. Before release, install a fixed Git tag into a temporary directory and
run:

    python -B scripts/validate_skill.py --installed-skill <temporary-install-directory>

The check compares relative file sets and SHA-256 values without printing file contents,
hashes, or sensitive data. Replacing an existing global skill still needs explicit S2
authorization. Git push, login, download, and upload each remain independent S3 actions.

## Development and Evaluation

    python -B scripts/validate_skill.py
    python -B -m unittest discover -s tests -v

The repository uses only the Python standard library. The validator checks structure,
frontmatter, conditional-reference links, sensitive patterns, and optional deployment
parity; tests cover deterministic contracts. The independent protocol at
evaluations/forward-eval.md must use a fresh agent and a synthetic temporary workspace.
Until it is run, release notes may claim only "local contract validation completed,"
not behavior validation.

## Changelog

| Version | Date | Changes |
| --- | --- | --- |
| v0.1.1 | 2026-09-15 | Short router, conditional references, explicit S1-S4 gates, fixed limits, release-parity validation, forward-eval protocol |
| v0.1.0 | 2026-09-08 | Initial release |

## License

[MIT](LICENSE)
