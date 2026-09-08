# Output Contract

Use the following order for a normal run:

1. Scope echo and material inventory.
2. Audit findings with verified, derived, unverified, or blocked labels.
3. Audit retrospective and root-cause analysis.
4. Ordered solution plan with dependencies, safety level, rollback, and acceptance.
5. Operation-specific authorization request.
6. Execution log and independent verification evidence.
7. Relative evaluation, residual risks, and second-cycle condition.

For file outputs, prefer a new run directory or an explicit output path. Preserve the
source by default and record input/output names, hashes when useful, tool versions,
commands, and known limitations. Do not store full sensitive source text when a short
redacted excerpt or hash is enough.

Evaluate these dimensions independently:

- completeness;
- correctness and internal consistency;
- traceability and citation readiness;
- format and rendering integrity;
- reproducibility;
- safety and privacy.

Use pass, partial, fail, or unknown; explain the evidence and do not convert unknowns
into numeric certainty or an AI-authorship probability.
