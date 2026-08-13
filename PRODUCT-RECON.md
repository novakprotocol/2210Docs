# Documentation Product Reconnaissance

## Objective

Study established documentation products to identify the user problems they solve, then implement an original Python-native controlled-document product. This is capability reconnaissance, not source-code or visual copying.

Research snapshot: August 2026.

## Capability findings

| Product family | Capability worth understanding | IaT Docs Engine response |
|---|---|---|
| MkDocs | Simple Markdown configuration, theme system, plugins, local preview, generated search | Keep the simple authoring loop; own our configuration, compiler, theme, validation, and local server |
| Sphinx | Structured domains, cross-references, extensibility, multiple builders, link checking | Add controlled cross-reference and builder concepts over time, without adopting reStructuredText or Sphinx |
| Docusaurus | Versioned documentation, hierarchical docs, plugins, MDX/React components | Add version channels and modular content later; avoid a Node/React/MDX dependency and active author content |
| GitBook | Branch/change-request review, Git synchronization, readable knowledge product, stale-content attention | Use native Git branches/PRs, visible revisions, review gates, freshness checks, and AI contracts inside private GHE |
| Antora | Distributed sources, components, versions, branches/tags, independently developed UI bundle | Future collection layer can aggregate approved repositories and versions while preserving one controlled theme |
| VitePress / Starlight | Fast static output, polished navigation, local search, responsive themes, plugin ecosystems | Preserve fast static output and reader quality while keeping a Python-only build and controlled JavaScript surface |
| Docsify | Immediate client-side Markdown rendering and very low setup | Retain low setup, but precompile HTML so release validation, hashes, provenance, and reliable offline behavior are possible |
| Material-style documentation themes | Strong navigation, device responsiveness, search, readable callouts | Implement only the reader capabilities needed for GS-2210 controlled work; do not copy visual systems |

## What common products generally optimize for

Most documentation products optimize for one or more of these goals:

1. Fast creation of attractive developer documentation.
2. Multi-page navigation and search.
3. API or source-code reference generation.
4. Versioned product documentation.
5. Collaborative editing and review.
6. Multi-repository aggregation.
7. Extensible themes and plugins.
8. Publishing to public web infrastructure.

Those are useful, but they do not by themselves solve controlled federal operating-document requirements.

## Gaps IaT Docs Engine is designed to address

### Controlled document identity

The page must expose a document ID, type, profile, version, status, owner, steward, original creator, effective date, last review, required review, repository, and template/engine version.

### Revision and approval evidence

A Git log is not enough for a reader. The rendered document needs a controlled revision register with the material change, editor, reviewer, approver, date, status, and controlling reference.

### Source-material classification

An AI must not treat every attachment as authoritative or every prior document as an example. The source register records role, permitted use, authority, restrictions, and disposition.

### Reader continuity

Long SOPs and IOPs need automatic furthest-read tracking, multiple named bookmarks, editable ticket/change/incident references, notes, and exact-position restoration after a publication update.

### Source-of-truth discipline

The live Pages document is the authoritative reading surface. The repository and PR workflow are the controlled authoring/evidence source. The reader deliberately avoids print/export/document-download controls that encourage unmanaged detached copies.

### Work attribution

Page-visible Git activity, words touched, changed sections, and Work Ledger mappings help show attributable work. The product explicitly prevents those metrics from masquerading as a standalone quality or personnel rating.

### AI-governed generation

The engine repository contains an ordered AI contract, 22 document profiles, a 32-module library, source-classification rules, machine-readable schemas, and deterministic scaffolding. The AI must fill gaps honestly rather than invent authority or production facts.

## Product differentiation

| Capability | Typical docs generator | IaT Docs Engine |
|---|---|---|
| Static site generation | Yes | Yes, Python-native |
| Markdown | Yes | Yes, with controlled semantic callouts and active-content rejection |
| Generic theme | Usually | Controlled GS-2210 manual reader |
| Formal document control | Limited/custom | First-class |
| Revision editor/reviewer/approver | Usually Git-only | First-class page data plus Git evidence |
| Source authority classification | Rare | First-class |
| Release authorization gates | Generic CI | Controlled-document release mode |
| Multiple editable reading bookmarks | Uncommon | Built-in |
| Ticket/change reference on bookmarks | Uncommon | Built-in |
| Furthest-read return marker | Uncommon | Built-in |
| Update notice with exact resume | Uncommon | Built-in |
| Contribution/Work Ledger evidence | Not typical | Built-in generation and display |
| AI contract and profile selection | Usually external | Repository-native |
| No detached-copy reader controls | Not typical | Contractual |
| Private GHE-first | Possible | Primary deployment model |

## Build-versus-buy decision

A generic framework would reduce initial compiler work, but it would also impose its configuration model, plugin lifecycle, theme assumptions, dependency chain, migration cadence, and security surface. Our distinguishing requirements already sit above the framework layer and would require extensive overrides.

The recommended decision is:

- build and own IaT Docs Engine;
- use small, well-understood low-level libraries rather than a documentation framework;
- preserve a clean migration boundary around those libraries;
- implement features in capability order, not competitor order;
- retain the earlier static template as migration input, not as the future engine.

## Features to adopt conceptually

### Near term

- deterministic content graph and stable cross-references;
- better link checking and orphan detection;
- multi-file manual source while retaining a one-manual reading mode;
- version channels and supersession banners;
- collection/catalog builds from approved derived repositories;
- stronger accessibility test automation;
- extension hooks with an allowlist and deterministic build contract;
- diagram and table asset registration;
- stale-content and review-due reporting.

### Later

- controlled multilingual builds;
- API/OpenAPI and inventory adapters;
- reusable approved snippets with provenance;
- authenticated server-side bookmark synchronization as an optional separate service;
- controlled browser authoring that always creates a branch/PR rather than editing Pages;
- organization-level dashboard for document health, review status, drift, and Work Ledger evidence.

## Explicit non-goals

- cloning another product's theme or interaction design;
- using public SaaS as the system of record;
- enabling uncontrolled inline editing of the Pages output;
- embedding credentials or production state in documentation;
- making contribution percentages a performance score;
- building a general-purpose website CMS before the controlled-document core is stable.

## Public sources reviewed

- MkDocs official documentation: https://www.mkdocs.org/
- Sphinx official documentation: https://www.sphinx-doc.org/
- Docusaurus official documentation: https://docusaurus.io/docs
- GitBook documentation: https://gitbook.com/docs
- Antora documentation: https://docs.antora.org/
- VitePress documentation: https://vitepress.dev/
- Astro Starlight documentation: https://starlight.astro.build/
- Docsify documentation: https://docsify.js.org/
- GitHub Pages custom workflow documentation: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
