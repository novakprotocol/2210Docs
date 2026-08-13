# Clean-Room Product Reconnaissance Rules

## Purpose

IaT Docs Engine may learn from public product capabilities without copying another product's protected implementation or identity.

## Allowed reconnaissance

- Read public product documentation and public capability descriptions.
- Use publicly accessible demos to understand user workflows.
- Record the user problem, expected outcome, and broad interaction pattern.
- Compare documented inputs, outputs, deployment models, dependencies, and limitations.
- Create a neutral capability matrix using original wording.
- Implement an independently designed solution using our architecture, data model, naming, theme, and code.
- Retain links and dates for the public sources reviewed.

## Prohibited conduct

- Copy or adapt source code from another product without an explicit, reviewed licensing decision.
- Copy HTML templates, CSS, JavaScript, icons, artwork, logos, distinctive layouts, wording, schemas, or sample content.
- Decompile or bypass access controls.
- Reproduce proprietary APIs or hidden behavior through reverse engineering.
- Present another product's feature name, branding, or visual identity as ours.
- Train an AI on private or restricted source material for implementation reuse.

## Required implementation record

For each substantial feature inspired by reconnaissance, record:

1. The user problem.
2. Public sources reviewed.
3. The abstract capability learned.
4. Our independent design decision.
5. Files changed.
6. Tests performed.
7. Licensing/security review when a new dependency is introduced.

## Dependency rule

Prefer the Python standard library. A third-party dependency may be added only when it is:

- substantially lower-level than the product;
- actively maintained enough for the intended environment;
- available under a reviewed license;
- pinned to a tested version;
- documented in `THIRD-PARTY-NOTICES.md`;
- replaceable behind a narrow internal interface.

A documentation framework is not a low-level dependency for this product and must not be introduced without an explicit architecture decision that supersedes this rule.

## Visual-design rule

The reader must remain an original controlled-manual interface. Similarity at the level of ordinary web conventions—navigation, search, buttons, dark mode—is acceptable. Recreating another product's distinctive visual composition is not.

## Evidence rule

Reconnaissance findings belong in `PRODUCT-RECON.md` or an approved research record. Code comments should describe our design, not claim compatibility or derivation from a competitor.
