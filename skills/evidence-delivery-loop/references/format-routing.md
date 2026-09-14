# Format Routing

Use capability discovery before choosing a processor. Match actual file type, requested
outcome, and installed capability. Read the safety matrix before crossing an input,
network, or write boundary.

| Input | Preferred capability | Required evidence |
| --- | --- | --- |
| Markdown, text, JSON, YAML, CSV, source code | Safe text or structured inspection | Extracted content and checked structure |
| CSV, TSV, XLSX | Spreadsheet capability | Formulas, sheets, values, and representative render checks |
| DOCX | Document capability | Extracted structure plus rendered-page inspection |
| PDF | PDF capability | Text or page extraction plus rendered-page inspection |
| PPTX | Presentation capability | Slide structure plus representative slide renders |
| IPYNB | Notebook capability | Cell structure; execution only with explicit authorization |
| Public URL | Least-powerful web fetch or browser capability | URL, retrieval time, and source evidence |
| Login-gated URL | Authorized Playwright or browser session | User-visible authorization and no credential extraction |
| ZIP, TAR, RAR, 7z archives | List the archive member manifest first; parse only confirmed inner scope | Manifest, bounded processing record, and inner-file routes |
| PNG, JPG, SVG, and other images | Image inspection or installed OCR | Visible-content description; partial without OCR |
| Audio, video | Out of scope; report capability_gap | State that transcription or frame analysis is unavailable |
| MSG, EML email files | Email parser or generic text extraction | Headers, body, attachment listing, and redaction |

For an archive, list the archive member manifest first, not the enclosing filesystem
directory. After the user confirms the inner scope, use only a bounded temporary parser
unless S1 authorizes a retained extraction. The limits are at most 500 members, 250 MiB
cumulative extracted size, and a 50:1 compression ratio; they aggregate across all
nested archives and must not reset per inner archive. Do not process encrypted archives
or an unrecognized archive format.

Do not infer successful rendering, execution, or download from file presence alone.
When a capability is unavailable, return capability_gap with the blocked claim, impact,
and smallest safe next step. When a capability fails at runtime, record the processor
and error summary, label the material blocked, and use a generic text fallback only
when it is safe. Label that fallback partial; one processor failure does not abort the
remaining audit.
