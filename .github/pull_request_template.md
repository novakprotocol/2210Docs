## Controlled manual change

### Change summary

Describe the operating, technical, governance, or presentation change.

### Document-control impact

- [ ] Manual content changed
- [ ] Document metadata changed
- [ ] Last-review or required-review date changed
- [ ] Controlled revision entry added or updated
- [ ] Creator or Work Ledger mapping changed
- [ ] Shared template shell changed
- [ ] AI contract, profile catalog, schema, or generator behavior changed

### Review

- [ ] Technical accuracy reviewed
- [ ] Owner/steward review completed
- [ ] Approval evidence linked when required
- [ ] Stop conditions, rollback, and validation remain explicit

### Generated evidence

- [ ] Repository size and contribution evidence refreshed
- [ ] Work Ledger integration records refreshed
- [ ] Contributor aliases and mappings reviewed
- [ ] Current version matches the controlled revision register

### Reader controls

- [ ] Read section 1 works
- [ ] Automatic furthest-read progress advances while reading downward
- [ ] Automatic progress does not move backward during review
- [ ] Translucent Return to furthest read marker appears and clears correctly
- [ ] Red Bookmark percentage updates with the current position
- [ ] Multiple quick and named bookmarks can be saved, opened, edited, moved, and removed
- [ ] Bookmark labels, ticket/change/incident/request/task/PR/issue references, and notes persist correctly
- [ ] New-build notice and browser refresh restore the exact viewed location
- [ ] Edit menu targets this manual repository
- [ ] No splash or detached-copy control was introduced

### AI and template conformance

- [ ] `AGENTS.md` operating mode was followed
- [ ] Shared template content remains generic, or this change is in a separate derived repository
- [ ] Applicable document profile and modules are identified
- [ ] No legacy subject-specific content was introduced into the shared template
- [ ] `ai/template-contract.json` requirements remain satisfied

### Validation

```text
python -m iatdocs --repo . build --strict
python -m iatdocs --repo . validate --built
```
