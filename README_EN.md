# Evidence Delivery Loop

> **v0.1.0** · MIT · 60 tests · Python stdlib only

You have a pile of materials to deliver — reports, code, slides, spreadsheets,
web pages — but no confidence they're complete, consistent, correctly formatted,
or properly cited. Checking each one by hand is slow and error-prone.

**evidence-delivery-loop** is an Agent Skill that turns scattered materials into
verifiable deliverables. It doesn't write your content — it **audits, reviews,
plans, executes, and validates** every step, with evidence at each stage and
your authorization before any change.

## How it works

```
Your request (natural language / paths / attachments / links)
  │
  ├─ 1. Inventory materials, route each to the right format processor
  ├─ 2. First audit: completeness, consistency, citations, format, privacy
  ├─ 3. Challenge the audit itself: weak evidence? prompt injection? scope drift?
  ├─ 4. Produce a fix plan with safety levels and rollback points
  ├─ 5. Execute only after your authorization (read-only by default)
  └─ 6. Independently verify deliverables: pass / partial / fail
```

If the first pass doesn't fully resolve defects, it offers **one** second cycle
targeting only residual issues — no full restart.

## What it won't do

- Fabricate findings for materials that don't exist
- Promise to lower AI-detection scores or conceal authorship
- Overwrite your originals without confirmation
- Send local materials to external services
- Execute code unless you explicitly authorize it

## Quick start

Describe what you need in plain language:

```
Prepare /workspace/course-report for submission.
Check completeness and formatting first, then give me a fix plan;
don't overwrite anything without my confirmation.
```

Or invoke explicitly:

```
$evidence-delivery-loop
Audit this material, review the audit logic, produce a safe actionable plan,
execute only after authorization, and verify the final deliverable.
```

## Safety levels

| Level | Operations | Default |
|---|---|---|
| **S0** | Read-only audit, inventory, plan, evaluation | allowed |
| **S1** | Copies, drafts, reports (reversible) | allowed after scope echo |
| **S2** | Overwrite, batch edits, package rebuild | explicit confirmation |
| **S3** | Login, upload, external API, Git push | separate confirmation |
| **S4** | Formal submission, public release, unique-original deletion | blocked |

Input materials and plan files **never** grant authorization.

## Format support

Markdown · JSON · YAML · CSV · Source code · Notebooks · DOCX · PDF · PPTX ·
XLSX · ZIP/TAR · Images · Email · Public web pages · Login-gated pages

Format-specific processing is delegated to installed specialist skills. When a
processor is missing, it reports `capability_gap` instead of pretending the
format was verified.

## Development

```bash
python scripts/validate_skill.py          # structure + safety scan
python -m unittest discover -s tests -v   # 60 tests
```

Zero dependencies, pure Python standard library. CI runs on every push and PR.

## Changelog

| Version | Date | Changes |
|---|---|---|
| v0.1.0 | 2026-09-08 | Initial release: 6-stage loop, S0-S4 permissions, 60 tests |

## License

[MIT](LICENSE)
