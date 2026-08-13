# Mandatory Instructions for AI, GPT, Coding Agents, and Automated Authors

This repository is the canonical **IaT Docs Engine and GS-2210 controlled-document contract**.

An AI or automation tool directed here must read, in order:

1. `AGENTS.md`
2. `AI-ENTRYPOINT.md`
3. `AI-GENERATION-CONTRACT.md`
4. `GHE-WEB-TEMPLATE-STANDARD.md`
5. `ai/template-contract.json`
6. `ai/document-profiles.json`
7. `2210-DOCUMENT-PROFILES.md`
8. `AUTHORING-GUIDE.md`
9. `section-library/2210-master.md`
10. `data/document.json`
11. `content/index.md`

## Determine the operating mode first

### Mode A — Maintain the canonical engine

Use this mode only when the request explicitly changes the compiler, controlled theme, contracts, schemas, profiles, validators, migration logic, or release workflows.

- Keep `content/index.md` generic across GS-2210 document classes.
- Do not insert a subject-specific SOP, IOP, command set, site inventory, system configuration, or prior controlled document into the canonical engine repository.
- Keep synthetic profile examples under `examples/`.
- Preserve the reader contract, source classification, validation, update behavior, Git intelligence, and migration path.
- Increment `TEMPLATE_VERSION` and engine-version references for a controlled release.
- Run `python -m iatdocs --repo . validate --built` after building.

### Mode B — Create or edit a derived controlled document

This is the normal mode.

- Create or use one separate **private** repository for the actual controlled artifact.
- Select the closest profile from `ai/document-profiles.json`.
- Run `python -m iatdocs --repo . init ...` for deterministic profile-driven scaffolding.
- Configure `data/document.json`.
- Replace instructional modules under `content/` with verified subject content.
- Classify every supplied source in `source-material-register.json`; an attachment is not automatically authoritative and is not automatically an example.
- Record material releases in `data/revisions.json`.
- Use a branch and pull request for material changes.
- Run `python -m iatdocs --repo . metrics --apply`, `validate`, and `build`.
- Enable the derived repository’s release-gate variable only after approvals and effective status are complete.

## Non-negotiable reader contract

A derived controlled page must retain:

- Direct entry with no splash screen.
- Sticky header and responsive left navigation.
- GHE repository size, last-review date, and review-due date as plain upper-left text.
- The governed fixed upper-right graphic loaded only from the approved central asset URL in `theme/assets/css/manual.css`.
- No reader-visible spelling of the graphic/program name; the approved asset URL is the only textual occurrence permitted.
- Light and dark themes.
- Full-section filtering, active navigation, and reading progress.
- Automatic furthest-read tracking beginning at section 1.
- A translucent return marker while the reader is above the furthest-read position.
- A red **Bookmark N%** control.
- Up to 20 browser-local bookmarks with editable label, ticket/change/incident/request/task/PR/issue reference, note, and exact position.
- The exact update lead text **Update available — refresh your browser** and position restoration after refresh.
- Repository Edit links for content, document control, and revision history.
- Page-visible creator, controlled revisions, Git activity, contribution metrics, and Work Ledger mapping status.
- No reader-facing print, export, document-download, copy-package, or detached-copy controls.
- The live Pages site as the authoritative reading surface and Git as the controlled editing/evidence source.

## Content and safety contract

- Never commit credentials, secrets, tokens, certificates, protected information, unnecessary live endpoints, or internal inventories.
- Sanitize examples, commands, diagrams, and images.
- Do not use the document itself as an access grant, execution authorization, or change approval.
- Keep policy authority, work authorization, live state, and evidence systems distinct.
- Use separate Pass, Fail, Not applicable with authority, and Incomplete outcomes where verification applies.
- Preserve original creator identity separately from later contribution activity.
- Treat contribution metrics as repository-activity evidence, not a quality score or standalone personnel-performance measure.
- Do not add script elements, inline event handlers, forms, iframes, embedded objects, or `javascript:` URLs to document Markdown.

## Completion commands

Canonical engine/template validation:

```powershell
python -m pip install -r requirements.txt
python -m iatdocs --repo . build --strict
python -m iatdocs --repo . validate --built
```

Derived release candidate:

```powershell
python -m iatdocs --repo . metrics --apply --require-ghe
python -m iatdocs --repo . build --release --strict
```

Do not report completion when a required command fails. State the exact blocker.
