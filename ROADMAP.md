# IaT Docs Engine Roadmap

## Version 0.08.2 — Functional foundation

Delivered:

- Python CLI and repository configuration;
- controlled single-manual compiler;
- Markdown security scanning and semantic callouts;
- stable anchors, navigation, search index, and source map;
- controlled reader theme;
- multiple editable bookmarks and furthest-read tracking;
- update notification with location restoration;
- document control, revisions, contribution evidence, and Work Ledger presentation;
- source-material classification and release validation;
- local build/serve/watch workflow;
- build manifests, hashes, receipts, and `.nojekyll` output;
- profile-driven scaffolding and v0.07 migration.

Exit criteria: reproducible build, zero structural test failures, validated generic seed, and a successful derived-document and migration test.

## Version 0.09 — Harden the compiler

- complete JSON Schema validation without external framework coupling;
- cross-file anchor and reference graph;
- link checker with internal/external policy modes;
- orphaned-section and duplicate-control detection;
- deterministic asset registry and image-alt validation;
- stricter HTML sanitizer and allowlist;
- richer structured diagnostics with file/line locations;
- Windows-first installer/bootstrap helper;
- signed or checksum-verified release bundle;
- accessibility automation and keyboard regression tests.

## Version 0.10 — Multi-file manual sources

- split a manual across controlled Markdown files;
- explicit navigation manifest or generated ordering;
- one-manual reading mode plus optional page routes;
- global search across all source files;
- stable cross-file references;
- per-section edit links and source provenance;
- incremental builds.

## Version 0.11 — Version and lifecycle channels

- current, draft, superseded, archived, and retired channels;
- version selector and supersession banner;
- immutable release snapshots with a current pointer;
- migration and compatibility matrix between engine versions;
- document-health and review-due reports.

## Version 0.12 — Collection and catalog layer

- aggregate approved derived repositories into an organization catalog;
- repository discovery from an explicit allowlist;
- document ID, profile, owner, status, review date, and risk facets;
- cross-document search and relationship graph;
- duplicate/superseded authority detection;
- collection build receipts and provenance.

## Version 0.13 — Controlled extension system

- Python entry-point based plugins;
- allowlisted build hooks;
- deterministic plugin ordering;
- plugin metadata, compatibility, and security policy;
- adapters for diagrams, OpenAPI, inventory catalogs, and data tables;
- no arbitrary client-side code injection.

## Version 0.14 — AI and evidence expansion

- machine-readable content completeness report;
- authority and evidence gap detection;
- source-to-claim traceability;
- proposed-change impact report;
- stale-content and drift detection;
- controlled AI review package that never auto-approves a release.

## Version 1.0 — Production baseline

Required before 1.0:

- stable compiler and configuration contract;
- documented support and migration policy;
- reproducible release packaging;
- successful GHE Pages publication in the target environment;
- complete keyboard and screen-reader acceptance tests;
- tested Windows and RHEL workflows;
- security review and threat model;
- derived-repository update process;
- operational runbook and recovery procedure;
- at least three different document profiles proven end to end.

## Deferred possibilities

- optional authenticated cross-device bookmark synchronization;
- browser authoring that creates a branch and PR;
- controlled localization;
- organization-wide document-health and contribution dashboards;
- integration adapters for ServiceNow and Work Ledger systems.

These remain separate components so the static Pages reader does not become a credentialed application surface.
