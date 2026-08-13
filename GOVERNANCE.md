# IaT Docs Engine Governance

## Operating model

The canonical engine repository controls the Python compiler, theme, reader behavior, GS-2210 profiles, schemas, validation, evidence generation, migration, and publication contract. Every actual SOP, IOP, MOP, runbook, work instruction, standard, design, plan, playbook, training package, catalog, knowledge article, manual, or other controlled artifact is maintained in a separate private derived repository.

## Control ownership

| Control area | Responsible role | Minimum rule |
|---|---|---|
| Compiler and theme | Engine maintainers | Review, version, test, and document changes. |
| Controlled content | Document steward and technical owner | Edit the derived repository through a branch and pull request. |
| Source classification | Author and reviewer | Record source role and permitted use; do not infer authority from attachment. |
| Creator attribution | Document owner | Preserve the original creator separately from later Git activity. |
| Review dates | Document steward | Maintain last-review and required-review dates. |
| Controlled revisions | Editor, reviewer, approver | Record material releases with version, date, summary, and evidence reference. |
| Repository size | Automated workflow | Measure through authenticated GHE API data. |
| Contribution evidence | Workflow plus document owner | Generate from controlled paths and maintain identity mappings. |
| Work Ledger records | Workflow and Work Ledger owner | Keep root-level records aligned to the measured commit. |
| Pages publication | Repository owner | Deploy the generated `site/` artifact; retain private visibility unless formally changed. |

## Source of truth

The live Pages site is the controlled reading copy. Git content, pull requests, approvals, revision records, and build receipts are the controlled editing and evidence source. Saved captures and detached copies are uncontrolled unless a separate records process controls them.

## Reading data

Bookmarks and furthest-read state remain browser-local. They are not committed, sent to Work Ledger, or shared with other readers. A refresh after an update notice preserves and restores the exact current location.

## Metrics use

Creator status and contribution percentages do not prove approval authority, quality, correctness, difficulty, operational value, or overall employee performance. Work Ledger output is supplemental attributable activity evidence and must be interpreted with other evidence.

## Release gates

A derived release requires complete document control, classified sources, no placeholders, a current revision matching the version, required review and approval, an effective date, authenticated repository size, generated contribution evidence, resolved or accepted Work Ledger mappings, passing content/security checks, working reader controls, and a validated build manifest.

## Engine propagation

Derived repositories do not retain automatic inheritance from the canonical repository. Engine updates are applied through an explicit migration/update process with dry-run planning, backups, document-owned path preservation, and post-update validation.
