# Output Contract

Use this response order:

1. Scope echo and material inventory.
2. Findings with verified, derived, unverified, or blocked labels.
3. Audit retrospective and root-cause analysis.
4. Ordered solution plan with dependencies, safety level, rollback, and acceptance.
5. Operation-specific authorization request.
6. Authorized execution log and independent verification evidence.
7. Relative evaluation, residual risks, and second-cycle condition.

Without S1 authorization, keep the complete audit, plan, and evaluation in the
conversation. Do not automatically create a report, copy, run directory, or retained
extraction. A material count does not itself authorize a local output.

After S1 authorization, use a new named run directory or explicit output path. Preserve
sources by default and record input and output names, hashes when useful, tool versions,
commands, and known limitations. Use redacted excerpts or hashes instead of full
sensitive source text.

Scale response detail to material count. For five or fewer items, include the full
contract in the conversation. For six to twenty items, summarize inventory and findings
there and place full evidence in an S1-authorized report. Above twenty items, lead with
a categorized summary and critical findings, then place the complete report in a file
only after the S1 gate is satisfied. End with actionable next steps.

Evaluate completeness, correctness and internal consistency, traceability and citation
readiness, format and rendering integrity, reproducibility, and safety and privacy.
Use pass, partial, fail, or unknown; explain evidence and do not convert unknowns into
numeric certainty or an AI-authorship probability.
