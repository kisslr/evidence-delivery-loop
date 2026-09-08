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

Do not infer successful rendering, execution, or download from file presence alone.
When a capability is unavailable, return capability_gap with the blocked claim, impact,
and smallest safe next step.

Use generic text inspection for unsupported textual formats, but label the result as
partial when a format-specific parser or renderer is required.
