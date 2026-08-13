# IaT Docs Engine

**IaT Docs Engine** is a Python-native compiler, controlled-document contract, and GitHub Enterprise Pages reader for GS-2210 technical artifacts.

It is not MkDocs, Jekyll, Sphinx, Docusaurus, Docsify, Antora, VitePress, Starlight, or a skin placed on another documentation framework. The engine reads repository Markdown and governed JSON, applies the GS-2210 contract, renders the controlled reader, validates the result, and emits a self-contained static `site/` artifact.

## Status

Version **0.08.2** is a functional foundation/MVP, not a finished 1.0 product. It currently provides:

- a Python CLI named `iatdocs`;
- deterministic profile-driven GS-2210 document scaffolding;
- Markdown parsing with stable unique heading anchors;
- semantic callouts for controls, warnings, stop conditions, evidence, notes, and template instructions;
- a controlled single-manual reader with responsive navigation and full-section filtering;
- automatic furthest-read tracking and a translucent return marker;
- up to 20 editable browser-local bookmarks with a controlled-record reference and note;
- update detection using `site-version.json`, with exact-location restoration after refresh;
- creator, revision, Git-activity, contribution, and Work Ledger presentation;
- repository-size and review-date presentation as plain header text;
- source-material classification, content security checks, release gates, manifests, hashes, and receipts;
- a local development server with source watching and browser reload;
- migration support for the earlier v0.07 Jekyll-derived repository layout;
- a custom GitHub Pages publication workflow.

The current release supports the **single-manual** build mode. Multi-page collections, cross-repository aggregation, version channels, localization, a packaged plugin SDK, and a browser authoring surface are roadmap items.

## Product model

```text
Canonical IaT Docs Engine repository
        │
        ├── Python compiler and CLI
        ├── GS-2210 profiles and module library
        ├── machine-readable AI contract
        ├── controlled reader theme
        ├── schemas and validation gates
        ├── migration and Git intelligence
        └── publication workflow
                 │
                 ├── private SOP repository
                 ├── private IOP repository
                 ├── private MOP repository
                 ├── private runbook repository
                 ├── private standard repository
                 └── other controlled 2210 repository
```

The canonical repository remains subject-neutral. Every actual SOP, IOP, MOP, runbook, standard, design, plan, job aid, or catalog is maintained in a separate private derived repository.

## Source-of-truth model

- **Live authenticated Pages site:** authoritative reading surface.
- **Git repository, branches, pull requests, approvals, revision data, and receipts:** controlled editing and evidence source.
- **Saved captures and detached copies:** uncontrolled unless a separate records process controls them.

The reader intentionally has no print, export, document-download, or copy-package control.

## Install for development

Python 3.11 or later is required.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --no-build-isolation -e .
```

A locked minimal runtime is also available:

```powershell
python -m pip install -r requirements.txt
```

When the package is not installed, run commands with `PYTHONPATH=src` on Linux/macOS or install it editable on Windows.

## Core commands

```powershell
# Confirm Python, dependencies, Git, gh, and repository configuration.
iatdocs --repo . doctor

# List the 22 controlled document profiles.
iatdocs --repo . profiles

# Compile the static site/ artifact.
iatdocs --repo . build --strict

# Validate source plus the generated reader.
iatdocs --repo . validate --built

# Build, serve, watch, and reload during authoring.
iatdocs --repo . serve --open

# Generate repository size, contribution, and Work Ledger evidence.
iatdocs --repo . metrics --apply

# Apply release gates and build a release candidate.
iatdocs --repo . release --require-ghe
```

## Create a derived document

1. Create a new **private** repository from this canonical repository.
2. Install the engine in that repository.
3. Select the closest profile.
4. Run a dry-run initialization.
5. Review the selected modules.
6. Re-run with `--apply`.

```powershell
iatdocs --repo . init `
  --profile iop `
  --document-id ITOPS-IOP-0001 `
  --title "Controlled Document Title" `
  --source-repository software/PRIVATE-DERIVED-REPOSITORY
```

Apply only in the derived repository:

```powershell
iatdocs --repo . init `
  --profile iop `
  --document-id ITOPS-IOP-0001 `
  --title "Controlled Document Title" `
  --source-repository software/PRIVATE-DERIVED-REPOSITORY `
  --apply
```

The command writes the selected modules to `content/index.md`, updates `data/document.json`, and creates the initial controlled revision in `data/revisions.json`. It backs up replaced files under `.template-backup/`.

## Repository layout

```text
.
├── src/iatdocs/                 Python compiler and CLI
├── theme/                       Controlled HTML/CSS/JavaScript reader
├── content/                     Subject Markdown owned by the derived document
├── data/                        Document, repository, revision, and contribution data
├── ai/                          Machine-readable AI and profile contracts
├── schemas/                     Controlled JSON schemas
├── section-library/             Reusable 2210 module catalog
├── starters/                    Profile-oriented starting sources
├── prompts/                     AI assignment prompt
├── tools/                       Git intelligence and revision helpers
├── tests/                       Engine and reader contract tests
├── work-ledger/                 Generated attributable activity evidence
├── site/                        Generated Pages artifact; do not author here
├── iatdocs.toml                 Project configuration
├── source-material-register.json
└── pyproject.toml
```

## Authoring inputs

The engine treats these as the primary controlled inputs:

- `content/index.md` — document body;
- `data/document.json` — identity, creator, ownership, lifecycle, repository, and reader data;
- `data/revisions.json` — formal revision, review, and approval register;
- `data/contribution-config.json` — identity and Work Ledger mappings;
- `source-material-register.json` — source role and permitted use;
- `content/attachments/` — sanitized supporting artifacts.

An attachment is neither automatically authoritative nor automatically an example.

## Generated output

A successful build emits:

```text
site/
├── index.html
├── 404.html
├── assets/
├── search-index.json
├── site-version.json
├── source-map.json
├── build-manifest.json
├── build-receipt.txt
└── .nojekyll
```

The build manifest records source and output hashes. The site-version record drives the browser update notice. The source map ties rendered headings back to source files.

## Reader behavior

The reader includes:

- direct entry without a splash screen;
- fixed header and responsive left navigation;
- GHE repository size, last review, and review due as ordinary text;
- a fixed approved upper-right watermark loaded from the central asset URL;
- light and dark themes;
- active-section navigation and full-section filtering;
- automatic furthest-read tracking;
- a translucent return marker when reviewing earlier content;
- a red `Bookmark N%` split control;
- multiple editable bookmarks with label, ticket/change/incident/request/task/PR/issue reference, note, and exact position;
- update detection and exact-position restoration;
- repository edit links;
- visible creator, revision, contribution, and Work Ledger evidence.

Bookmarks and reading position are browser-local. They do not synchronize across devices or accounts and are not sent to Work Ledger.

## Contribution evidence

The repository intelligence tool can calculate attributable Git activity for configured paths, including commits, words added, words removed, words touched, recent changes, sections changed, and comparable share.

These measurements are **activity evidence only**. They do not independently measure quality, accuracy, difficulty, approval authority, operational effect, or personnel performance.

## Security

Document Markdown is scanned for active HTML and unsafe constructs, including scripts, inline event handlers, forms, frames, embedded objects, `javascript:` URLs, and HTML data URLs. Examples and attachments must be sanitized. Credentials, secrets, tokens, protected data, unnecessary live endpoints, and unnecessary internal inventories remain outside Git.

See `SECURITY.md` and `source-material-register.json`.

## Product reconnaissance and design basis

The engine is being developed through clean-room capability reconnaissance: evaluate what documentation products make possible, identify the underlying user need, and implement an original Python-native solution appropriate for controlled GS-2210 documents.

See:

- `PRODUCT-RECON.md`
- `CLEAN-ROOM-RECON-RULES.md`
- `ARCHITECTURE.md`
- `ROADMAP.md`
- `NAME-DECISION.md`

## Rights

Original repository material is copyright © 2026 Matthew S. Novak. All Rights Reserved. See `COPYRIGHT-AND-RIGHTS.md`.

## Workstation helpers

```powershell
# Author with automatic rebuild and browser refresh.
.\SERVE-LOCAL.ps1

# Rebuild, test, publish gh-pages, configure Pages, and retain a receipt.
.\PUBLISH-PAGES.ps1
```

Both helpers use the offline runtime installed by the dual-host bootstrap when present. Otherwise they create a repository-local `.venv` and install the pinned runtime dependencies.

## Deployed canonical repository

- Repository: `novakprotocol/2210Docs`
- Host: `github.com`
- Pages: enabled from the generated `gh-pages` branch by the bootstrap package
- Template repository: enabled
