# GS-2210 Document Profiles

This guide maps common IT Specialist (2210) artifacts to the 32 reusable modules in `section-library/2210-master.md`. The machine-readable source is `ai/document-profiles.json`.

| Profile ID | Artifact | Purpose | Required | Recommended |
|---|---|---|---:|---:|
| `comprehensive-2210` | Comprehensive 2210 Controlled Document | Use the complete module library when the final artifact class has not been selected or when a broad engineering/operating package is required. | 31 | 0 |
| `sop` | Standard Operating Procedure | Establish repeatable operational policy, responsibility, execution, control, evidence, and review. | 25 | 6 |
| `iop` | Internal Operating Procedure | Define an internal operating method with explicit authority, baseline, approvals, verification, exception, and audit controls. | 26 | 5 |
| `mop` | Method of Procedure / Maintenance Plan | Control a bounded maintenance, implementation, migration, or change event from authorization through rollback and closeout. | 24 | 7 |
| `implementation-plan` | Implementation / Change Plan | Plan and govern a technical implementation with dependencies, sequencing, controls, tests, communications, evidence, and rollback. | 29 | 2 |
| `runbook` | Runbook | Guide routine diagnosis, execution, validation, restoration, handoff, and escalation at technician level. | 26 | 5 |
| `work-instruction` | Work Instruction | Explain a narrow, repeatable technician task with exact prerequisites, actions, results, evidence, and closeout. | 19 | 10 |
| `incident-playbook` | Incident Response Playbook | Guide detection, triage, containment, restoration, evidence preservation, communications, escalation, and after-action correction. | 29 | 2 |
| `emergency-procedure` | Emergency Operating Procedure | Authorize only bounded emergency response with minimum necessary action, rapid escalation, evidence, restoration, and post-event review. | 29 | 2 |
| `technical-standard` | Technical Standard | Define mandatory technical requirements, configuration baselines, approved options, validation, exceptions, and lifecycle control. | 22 | 9 |
| `system-design` | System / Service Design | Describe requirements, architecture, interfaces, data flows, dependencies, controls, operations, recovery, and tradeoffs. | 23 | 8 |
| `architecture-decision-record` | Architecture Decision Record | Record a significant technical choice, context, options, rationale, consequences, controls, and review triggers. | 19 | 11 |
| `test-validation-plan` | Test / Validation Plan | Demonstrate that requirements, controls, interfaces, recovery, performance, and acceptance criteria pass with attributable evidence. | 26 | 5 |
| `recovery-continuity-plan` | Recovery / Continuity Plan | Restore or sustain service through disruption with dependencies, RTO/RPO, communications, testing, evidence, and fallback. | 29 | 2 |
| `training-job-aid` | Training Package / Job Aid | Enable qualified performance through objectives, prerequisites, lessons, demonstrations, exercises, assessment, remediation, and references. | 25 | 6 |
| `governance-catalog` | Governance Standard / Catalog | Control definitions, ownership, approved options, data quality, lifecycle, change authority, metrics, and review. | 21 | 10 |
| `service-catalog-entry` | Service Catalog / Operating Model | Define a service, consumers, ownership, interfaces, service levels, support, controls, capacity, lifecycle, and request paths. | 21 | 10 |
| `data-reporting-procedure` | Data / Reporting Procedure | Govern data acquisition, transformation, quality, classification, release, lineage, records, metrics, and correction. | 26 | 5 |
| `security-control-plan` | Security / Privacy Control Plan | Define security, identity, privacy, audit, evidence, exception, monitoring, recovery, and recertification controls. | 28 | 3 |
| `monitoring-observability-plan` | Monitoring / Observability Plan | Define signals, thresholds, dashboards, alerting, ownership, triage, evidence, capacity, availability, and improvement. | 29 | 2 |
| `retirement-decommission-plan` | Retirement / Decommission Plan | Remove a system or service safely while preserving records, dependencies, data, access control, evidence, communications, and closure. | 28 | 3 |
| `knowledge-article` | Controlled Knowledge Article | Provide reviewed technical guidance without becoming an execution authority or uncontrolled procedure. | 17 | 14 |

## Modes

- **minimum** — required modules plus mandatory control modules.
- **recommended** — required and recommended modules; this is the default.
- **comprehensive** — every document module, followed by removal of non-applicable modules during authoring.

## Rules

- Select the closest approved profile.
- Retain required and mandatory control modules.
- Use recommended mode by default.
- Remove unused optional modules instead of publishing empty placeholders.
- Record Not applicable only with identified authority.
- Add a new module only when the need cannot be met by an existing module.

## Deterministic generation

```powershell
python -m iatdocs --repo . init --profile PROFILE-ID --document-id DOCUMENT-ID --title "TITLE" --source-repository OWNER/REPOSITORY
```

The command is dry-run by default. Add `--apply` only inside the separate derived repository.
