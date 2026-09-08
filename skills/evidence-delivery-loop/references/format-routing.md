# Format Routing

Use capability discovery before selecting a processor. Match the actual file type,
the user's requested outcome, and the installed skill inventory.

| Input | Preferred capability | Required evidence |
| --- | --- | --- |
| Markdown, text, JSON, YAML, CSV, source code | safe text or structured inspection | extracted content and checked structure |
| CSV, TSV, XLSX | spreadsheet capability | formulas, sheets, values, and representative render checks |
| DOCX | document capability | extracted structure plus rendered page inspection |
| PDF | PDF capability | text/page extraction plus rendered page inspection |
| PPTX | presentation capability | slide structure plus representative slide renders |
| IPYNB | notebook capability | cell structure; execution only with explicit authorization |
| Public URL | web fetch or browser capability | URL, retrieval time, and captured source evidence |
| Login-gated URL | authorized Playwright/browser session | user-visible authorization and no credential extraction |
| ZIP, TAR, RAR, 7z archives | extract to a bounded temp directory, then route each inner file | archive listing, extraction log, and inner-file routes |
| PNG, JPG, SVG, and other images | image inspection or OCR capability if installed | description of visible content; label as partial without OCR |
| Audio, video | out of scope; report capability_gap | state that transcription or frame analysis is not available |
| MSG, EML email files | email parsing capability or generic text extraction | headers, body text, and attachment listing; redact credentials |

Do not infer successful rendering, execution, or download from file presence alone.
When a capability is unavailable, return capability_gap with the blocked claim, impact,
and smallest safe next step.

When a capability exists but fails at runtime, record the error, label the material as
blocked with the processor name and error summary, and attempt a generic text fallback
if the format allows it. Label fallback results as partial. A single processor failure
does not abort the remaining audit.

Use generic text inspection for unsupported textual formats, but label the result as
partial when a format-specific parser or renderer is required.
