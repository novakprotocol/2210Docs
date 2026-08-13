# Security Model

## Static publication boundary

IaT Docs Engine produces static HTML, CSS, JavaScript, and JSON. The published reader must not require credentials beyond the authenticated GHE Pages boundary and must not contain repository tokens or API credentials.

## Prohibited source content

Do not commit:

- passwords, tokens, private keys, certificates, connection strings, or session material;
- protected health, personnel, privacy, or investigative information;
- transient tokenized raw-content URLs;
- unnecessary live production endpoints;
- unnecessary internal inventory or topology;
- unsanitized command output containing identifying or secret information.

## Markdown security

The compiler rejects active or document-level HTML constructs in controlled Markdown, including:

- scripts;
- iframes, objects, embeds, and applets;
- forms and interactive fields;
- inline event handlers;
- `javascript:` URLs;
- HTML data URLs and `srcdoc`;
- page-level meta, link, base, and style elements.

Raw HTML exists only for a constrained set of ordinary document markup and remains subject to scanning.

## Browser-local data

Reading progress and bookmarks are stored only in browser local storage. Bookmark labels, references, and notes may contain ticket identifiers, so users must avoid protected or secret content. The static reader does not transmit those values to the repository, Work Ledger, or a server.

## Dependency policy

Dependencies are pinned. New dependencies require license, maintenance, security, and replacement review. Documentation frameworks and arbitrary JavaScript packages are not accepted merely for convenience.

## Vulnerability reporting

Report a suspected vulnerability through the approved private organizational security channel. Do not place sensitive vulnerability details in a public issue or in the Pages content.
