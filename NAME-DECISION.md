# Product Name Decision

## Selected working name

**IaT Docs Engine**

- Product name: `IaT Docs Engine`
- Command: `iatdocs`
- Canonical repository: `ITOPS-IaT-2210-Docs-Engine`
- Generated-by identifier: `iatdocs`

## Meaning

`IaT` aligns the product with the Infrastructure-as-Truth operating model: the controlled repository is the versioned source, the compiler produces a deterministic reading surface, and changes are attributable and reviewable.

`Docs Engine` accurately describes the product boundary. It is not merely a theme or template; it compiles, validates, measures, and publishes controlled documentation.

## Rejected names

### GitDocs

Rejected as the official product name because the name is already used by multiple documentation and AI products and by internal documentation sites elsewhere. It remains a useful informal description but is not distinctive enough for the canonical product.

### Doc2210

Too narrow for the eventual compiler and collection layers, and the string already appears in unrelated product/document identifiers online.

### DocForge / GitTruth

Both are already used in other products or projects and do not identify the GS-2210 controlled-document model as clearly.

## Naming rule

Do not rename the product casually in derived repositories. A formal rename must update the package name, CLI, schemas, build identifiers, AI contract, migration compatibility, and release receipts together.
