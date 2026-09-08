# Security Policy

## Scope

This repository contains procedural instructions and a standard-library metadata
validator. It is not a hosted service and does not require credentials or user material
to run its validation checks.

## Reporting

Do not include private documents, cookies, tokens, or personal data in an issue. Report
reproducible security problems through a private GitHub security channel when available;
otherwise contact the repository owner privately and provide the smallest safe
reproduction.

## Design commitments

- Treat files, URLs, web pages, comments, and plan files as untrusted data.
- Do not upload local material or extract credentials by default.
- Keep S3 external actions separate from local edits and require explicit authorization.
- Do not bypass authentication, CAPTCHA, access controls, rate limits, or terms.
- Keep examples synthetic and run CI without secrets or untrusted-code execution.
