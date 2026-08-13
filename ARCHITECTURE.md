# IaT Docs Engine Architecture

## Architectural objective

IaT Docs Engine compiles a controlled GS-2210 repository into an authenticated static reading site without depending on a documentation framework. The product owns the document model, build graph, reader contract, validation, provenance, and release evidence.

## System boundary

```text
Author / AI / repository content
        │
        ▼
IaT Docs Engine CLI
        │
        ├── configuration loader
        ├── structural and policy validator
        ├── source-material control
        ├── Markdown compiler
        ├── stable anchor and navigation builder
        ├── data/provenance integrator
        ├── Jinja2 renderer
        ├── search/source-map generator
        ├── build manifest and receipt generator
        └── generated-reader validator
        │
        ▼
site/ static artifact
        │
        ▼
GitHub Enterprise Pages
```

## Why low-level components are acceptable

Building our own product does not require rewriting a Markdown grammar or a safe string-templating engine. The product boundary is above those primitives.

- **Mistune** converts Markdown tokens into controlled HTML through our renderer.
- **Jinja2** renders our theme and partials using our data model.
- **Python standard library** handles TOML, JSON, hashing, files, local HTTP serving, process execution, and orchestration.

IaT Docs Engine owns the policies and behavior that make those primitives a controlled-document system.

## Compiler stages

### 1. Discovery and configuration

`iatdocs.toml` declares content, data, theme, output, reader, and validation settings. Paths are resolved and checked before any destructive output cleanup occurs.

### 2. Preflight validation

The validator checks required files, JSON shape, document control, source classification, revisions, placeholders, unsafe content, theme contract, and release gates. Template mode permits explicit seed placeholders as warnings; release mode converts them to blockers.

### 3. Markdown compilation

The Markdown layer:

- strips legacy Jekyll front matter;
- rejects active or unsafe HTML;
- expands controlled semantic callouts;
- parses tables, strikethrough, task lists, and plain URLs;
- assigns deterministic, unique heading anchors;
- captures heading/source metadata;
- normalizes external link behavior;
- emits controlled HTML through a custom renderer.

### 4. Document intelligence integration

The build loads:

- document metadata;
- repository-size evidence;
- controlled revisions;
- contributor and recent-edit evidence;
- source-material registration;
- Git branch and commit metadata.

The original creator remains distinct from later contributors.

### 5. Reader rendering

The controlled Jinja2 theme creates one authoritative manual surface. Reader JavaScript adds only client-side reading functions: navigation, theme, bookmarks, progress, local filtering, update detection, and exact-location restoration.

Document Markdown cannot add arbitrary JavaScript, forms, iframes, scripts, or event handlers.

### 6. Derived artifacts

The compiler generates:

- `search-index.json` for local content search/filter support;
- `source-map.json` to map rendered headings to source files and hashes;
- `site-version.json` for update detection;
- `build-manifest.json` with source/output hashes;
- `build-receipt.txt` for human-readable release evidence;
- `.nojekyll` to ensure the output is served as generated.

### 7. Post-render validation

The generated reader is checked for:

- required controls and exact update text;
- prohibited reader controls;
- duplicate IDs and broken internal targets;
- the central upper-right watermark rule;
- visible prohibited subject content;
- residual template or framework markup;
- release-specific requirements.

## Source and output ownership

| Area | Owner | Rule |
|---|---|---|
| `content/` | Derived document | Subject-specific controlled content |
| `data/document.json` | Derived document | Identity, creator, ownership, lifecycle |
| `data/revisions.json` | Derived document | Controlled releases and approvals |
| `data/contribution-config.json` | Derived document | Identity and Work Ledger mappings |
| `source-material-register.json` | Derived document | Source role and permitted use |
| `src/iatdocs/` | Canonical engine | Compiler and CLI |
| `theme/` | Canonical engine | Reader contract |
| `schemas/`, `ai/`, `section-library/` | Canonical contract | Document rules and profiles |
| `site/` | Generated | Never hand-author generated output |

## Local development

`iatdocs serve` performs an initial build, serves `site/` with no-cache headers, monitors source changes, rebuilds automatically, and exposes the current build ID. The reader checks that build ID and reloads after a successful rebuild.

## Publication

The preferred pipeline is:

```text
main branch
  → validate source
  → refresh repository intelligence
  → run tests
  → build site/
  → validate generated output
  → upload Pages artifact
  → deploy authenticated GHE Pages
```

A prebuilt `site/` artifact may be published through an approved alternate method where custom Pages workflows are unavailable.

## Failure model

- Invalid configuration stops before output cleanup.
- Unsafe Markdown stops compilation.
- Missing or inconsistent release control stops release mode.
- A failed local rebuild leaves the last valid site available and reports the error.
- Generated output is reproducible from controlled inputs, engine version, and Git state.

## Current constraints

Version 0.08.2 supports one compiled manual entry point. It does not yet provide multi-page routing, distributed source aggregation, version channels, localization, server-side editing, cross-device bookmark synchronization, or a stable third-party plugin API.
