# GHE Web Template Standard

Every derived document is compiled by IaT Docs Engine and published as the generated `site/` artifact through an approved GHE Pages workflow. A page that merely resembles the reader is not compliant.

## Required reader behavior

- Direct entry; no splash screen.
- Persistent header and responsive left navigation.
- Plain upper-left text for GHE repository size, last review, and review due.
- Approved hosted graphic fixed in the upper-right below the header.
- Light and dark themes, full-section filtering, active navigation, and reading progress.
- Automatic furthest-read tracking that advances but does not move backward.
- Translucent `Return to furthest read` marker while reviewing earlier content.
- Red `Bookmark N%` control showing the current reading percentage.
- Up to 20 browser-local bookmarks with editable label, controlled-record reference, note, and exact position.
- `Update available — refresh your browser` notification with exact-location restoration.
- Repository Edit links for content, document control, and revisions.
- Page-visible creator, controlled revisions, recent edits, contribution metrics, provenance, and Work Ledger mapping status.
- No reader-facing print, export, document-download, copy-package, or detached-copy controls.

## Controlled compiler and theme

The Python package under `src/iatdocs/`, Jinja templates under `theme/templates/`, reader assets under `theme/assets/`, workflow, schemas, validators, and build manifest are engine-controlled. Document authors normally modify only the document-owned paths identified by `ai/template-contract.json`.

## Accessibility and resilience

The built document remains readable without JavaScript. Interactive features require keyboard operation, visible focus, usable labels, responsive behavior, and no page-level horizontal overflow. Accessibility conformance is a build/test obligation, not a styling claim.

## Publication

`main` contains controlled source. The build workflow installs pinned Python dependencies, generates repository intelligence, compiles `site/`, validates the output, uploads the Pages artifact, and deploys it. The generated output is never the editing source.
