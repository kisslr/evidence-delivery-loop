# Evidence Delivery Loop

evidence-delivery-loop is a process skill for Codex and compatible Agent Skills
implementations. It turns natural-language requests, paths, attachments, pasted text,
public links, and authorized browser material into an auditable and verifiable delivery.

## Workflow

```text
input and scope
  -> inventory and format routing
  -> first audit
  -> audit retrospective and root cause
  -> remediation plan
  -> plan and safety review
  -> authorized execution
  -> format, runtime, and evidence verification
  -> relative evaluation and one follow-up cycle
```

The skill does not invent findings for missing material, claim universal binary-format
support, or rewrite text to conceal provenance or evade AI detection. It governs scope,
authorization, evidence, and validation while specialized skills perform document,
PDF, presentation, spreadsheet, notebook, and browser operations.

## Low-barrier use

Provide a goal in ordinary language, a path, an attachment, pasted text, or a public URL.
The skill infers the likely route and asks only for information that materially changes
safety, scope, or acceptance.

Explicit invocation is also supported:

```text
$evidence-delivery-loop
Audit this material, review the audit logic, produce a safe actionable plan,
execute only after authorization, and verify the final deliverable.
```

## Safety

The default level is S0 read-only analysis. S1 copies and drafts are reversible. S2
overwrites and batch changes require confirmation. S3 external operations require a
separate confirmation. S4 formal submission, public release, unique-original deletion,
and production changes are blocked by default.

## Development

The first version uses only the Python standard library:

```text
python scripts/validate_skill.py
python -m unittest discover -s tests -v
```
