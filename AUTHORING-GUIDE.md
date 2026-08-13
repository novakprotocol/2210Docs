# 2210 Controlled Document Authoring Guide

## First setup

```powershell
python -m pip install -r requirements.txt
python -m iatdocs --repo . doctor
python -m iatdocs --repo . profiles
```

## Profile-driven start

In a separate private derived repository, run `python -m iatdocs --repo . init` with a profile ID, document ID, title, and source repository. The command is dry-run by default and refuses to place subject-specific content in a canonical engine/template path unless explicitly overridden for testing.

The generated Markdown is instructional scaffolding, not an effective controlled document. Replace instructions with verified content, remove non-applicable optional modules, and keep release gates open when facts, authority, evidence, review, or approval are incomplete.

## Authoring sequence

1. Create one private derived repository for one controlled artifact.
2. Classify supplied sources in `source-material-register.json`.
3. Select the closest profile from `ai/document-profiles.json`.
4. Run `iatdocs init` or copy a profile seed from `starters/` into `content/index.md`.
5. Complete creator, owner, steward, classification, review, approval, and repository fields in `data/document.json`.
6. Write controlled Markdown under `content/`; put sanitized supporting artifacts in `content/attachments/`.
7. Use a branch and pull request for material changes.
8. Record material releases in `data/revisions.json`.
9. Generate GHE size, Git contribution, and Work Ledger evidence with `iatdocs metrics --apply`.
10. Run `iatdocs build --strict` during drafting and `iatdocs build --release --strict` before an effective release.
11. Publish the generated `site/` artifact with the approved Pages workflow.

## Local authoring loop

```powershell
python -m iatdocs --repo . serve --open
```

The server rebuilds when controlled source changes and open pages reload when the build ID changes.

## Semantic callouts

The engine supports controlled Markdown directives without requiring authors to write theme HTML:

```markdown
::: warning Review required
This value requires technical-owner concurrence before release.
:::
```

Supported classes are `control`, `warning`, `stop`, `evidence`, `note`, and `template`.

## Content rules

Use objective steps, pass criteria, stop conditions, rollback, evidence, and authority boundaries. Do not include credentials, protected data, transient tokenized URLs, or unnecessary live endpoints. Make examples synthetic or sanitized. Define Pass, Fail, Not applicable with authority, and Incomplete as separate outcomes.
