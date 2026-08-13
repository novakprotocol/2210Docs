# Contributing

## Canonical IaT Docs Engine repository

Changes to the template must be generic, reusable, and backward-aware. A template pull request must identify:

- the contract requirement being added or changed;
- whether derived repositories require migration;
- controlled files affected;
- browser, mobile, accessibility, and validator results;
- template-version and manifest updates;
- any preserved document-owned files.

Subject-specific operational content does not belong in the canonical IaT Docs Engine repository.

## Derived document repository

Material content changes should use a branch and pull request. The pull request should identify:

- document ID and current version;
- sections changed;
- reason and controlling ticket/change/incident/request/task/issue;
- risk and operational effect;
- reviewers and approvers required;
- evidence and validation results;
- whether the change requires a new controlled revision.

Do not commit credentials, secrets, protected data, transient tokenized URLs, or unnecessary live endpoints.

## Public contribution rights

A submission intended for inclusion is accepted only under `CONTRIBUTOR-RIGHTS.md`. Do not submit material owned by an employer, government, client, or other party without written authority.
