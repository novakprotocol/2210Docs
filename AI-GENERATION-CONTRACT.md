# AI Generation Contract for GS-2210 Controlled Pages

## Purpose

This repository is both the Python-native compiler used by controlled-document repositories and the authoritative specification an AI must follow when creating or changing one of those repositories.

Pointing an AI here means:

> Use the IaT Docs Engine, GS-2210 profiles, source-classification rules, reader behavior, data model, and validation gates. Work in a separate private derived repository for the requested artifact. Do not redesign the reader or convert the canonical engine repository into the subject document.

## Controlled workflow

```text
User brief and supplied material
            │
            ▼
AI reads AGENTS.md and ai/template-contract.json
            │
            ▼
AI classifies every supplied source and selects a document profile
            │
            ▼
python -m iatdocs init creates deterministic modules in the derived repository
            │
            ├── content/*.md                 controlled subject content
            ├── data/document.json           identity and lifecycle
            ├── data/revisions.json          governed releases
            ├── source-material-register.json source role and permitted use
            ├── content/attachments/         sanitized supporting artifacts
            └── unchanged compiler/theme contract
            │
            ▼
Branch → pull request → review → approval → merge
            │
            ▼
python -m iatdocs metrics / validate / build
            │
            ▼
The generated site/ artifact is deployed to authenticated GHE Pages
```

## Engine ownership versus document ownership

The canonical engine repository owns compilation, semantic Markdown handling, reader behavior, theme, schemas, profiles, validation, Git intelligence, Work Ledger output, release receipts, and migration tooling.

Each derived repository owns its subject content, creator, permissions, review and approval, revision history, issues, pull requests, Pages publication, repository size, contributor mappings, supersession, and retirement.

## Source-material rule

Every supplied item must be explicitly classified in `source-material-register.json` as an authoritative source, approved operational source, supporting reference, worked example, layout-only example, superseded source, excluded/restricted item, or unverified item.

An AI may not infer that an attachment is authoritative or that it is an example merely because it was attached. Unverified material cannot silently supply release authority, facts, approval, or evidence.

## Machine-readable contract

- `ai/template-contract.json` defines controlled paths, required behavior, prohibited controls, and commands.
- `ai/document-profiles.json` maps 22 GS-2210 profiles to the controlled module library.
- `ai/derived-document-intake.schema.json` defines a standardized assignment brief.
- `source-material-register.json` records source role and permitted use.

## Acceptance principle

Visual similarity is not conformance. A compliant result must preserve the compiler inputs, data fields, source classifications, reader behavior, validation rules, release receipts, and source-of-truth model.
