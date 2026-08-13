## 1. Purpose and Controlling Principle

<p class="lead">State the exact operational outcome this procedure controls and the principle that governs every decision made under it.</p>

<aside class="callout control">
  <strong>Controlling principle</strong>
  <p>Replace this text with the non-negotiable rule that governs the procedure.</p>
</aside>

Describe why the procedure exists, the problem it controls, and the boundary between this procedure and other authorities.

## 2. Scope, Applicability, and Exclusions

<p class="lead">Define when the procedure applies, who may use it, and what must be handled through another process.</p>

| Included | Excluded or separately governed |
|---|---|
| Replace with an included platform, service, site, role, or condition. | Replace with an excluded condition and identify its controlling authority. |
| Add additional rows as required. | Do not leave exclusions implicit. |

## 3. Definitions and Controlled Terms

| Term | Controlled meaning |
|---|---|
| Replace term | Replace with the meaning used by this procedure. |
| System of record | Identify the authoritative source rather than relying on local interpretation. |

## 4. Authority, References, and System-of-Record Boundaries

<p class="lead">Identify what authorizes the work and which source controls policy, implementation state, evidence, and approval.</p>

| Layer | Purpose | Authoritative source |
|---|---|---|
| Policy | Defines the required control. | Replace with approved authority. |
| Request and approval | Authorizes the specific work. | Replace with ITSM, IAM, owner, or change authority. |
| Live state | Records what is implemented. | Replace with platform or configuration source. |
| Evidence | Proves what occurred and the result. | Replace with approved evidence repository. |

## 5. Roles, Qualifications, and RACI

| Role | Accountability | Required evidence |
|---|---|---|
| Process owner | Owns the procedure and material changes. | Approval and review record. |
| Implementer | Performs only authorized work. | Execution and before/after evidence. |
| Peer reviewer | Independently verifies scope and result. | Review record and disposition. |

## 6. Prerequisites and Controlled Baseline

<aside class="callout warning">
  <strong>Do not begin until prerequisites are satisfied</strong>
  <p>List every access, approval, backup, maintenance window, dependency, and rollback requirement that must exist before execution.</p>
</aside>

| Prerequisite | Pass criterion | Evidence |
|---|---|---|
| Approved controlling record | Scope, owner, risk, and authorization are complete. | Record identifier. |
| Qualified implementer | Training and role assignment are current. | Qualification record. |
| Known starting state | Current configuration and health are captured. | Before-state evidence. |

## 7. Request, Pre-Implementation Review, and Authorization

| Step | Action | Requirement | Evidence |
|---:|---|---|---|
| 1 | Open or verify the controlling record. | Use the approved request, incident, or change path. | Record ID. |
| 2 | Validate scope and ownership. | Stop when ownership or authority is unresolved. | Owner concurrence. |
| 3 | Review risk and rollback. | Define measurable stop and recovery conditions. | Approved plan. |

## 8. Internal Operating Procedure

<p class="lead">Write each action so another qualified technician can execute it without relying on undocumented knowledge.</p>

| Step | Action | Requirement | Evidence |
|---:|---|---|---|
| 1 | Capture before state. | Record the exact object, configuration, health, and dependencies. | Before-state artifact. |
| 2 | Perform the authorized change. | Do not broaden scope beyond the controlling record. | Command, log, or execution record. |
| 3 | Check immediate health. | Apply the defined stop condition when any gate fails. | Health result. |

<aside class="callout stop">
  <strong>Stop conditions</strong>
  <p>Replace this text with objective conditions that require the technician to stop, contain impact, notify the required roles, or initiate rollback.</p>
</aside>

## 9. Verification, Acceptance, and Audit Evidence

| Control ID | Verification | Pass criterion | Evidence |
|---|---|---|---|
| MAN-V01 | Identity and scope | Every object and principal resolves to the approved target. | Verification output. |
| MAN-V02 | Functional result | The intended service result is demonstrated. | Test result. |
| MAN-V03 | Independent review | A qualified reviewer confirms the evidence and disposition. | Reviewer record. |

## 10. Exception, Emergency, and Rollback Handling

| Required field | Minimum content |
|---|---|
| Exception ID | Unique identifier linked to the controlling record. |
| Reason | Why the standard path cannot be used. |
| Compensating control | What limits risk until closure. |
| Expiration | Date or condition that ends the exception. |

<aside class="callout stop">
  <strong>Emergency does not mean undocumented</strong>
  <p>Define the minimum record, authorization, evidence, notification, and retrospective review required during emergency work.</p>
</aside>

## 11. Monitoring, Drift Detection, Review, and Recertification

| Cadence | Owner | Review |
|---|---|---|
| At creation or material change | Implementer and peer reviewer | Full verification set. |
| Scheduled review | Process owner | Scope, authority, baseline, evidence, and exceptions. |
| Triggered review | Assigned owner | Incident, audit finding, platform change, or detected drift. |

## 12. Records, Metrics, and Evidence Retention

- Identify where records are stored and who may access them.
- Define retention, correction, and supersession rules.
- Measure control health and outcomes rather than raw activity alone.
- Keep operational evidence separate from unauthorized personnel records.

## 13. Training, Implementation, and Test-Readiness Plan

1. Replace all placeholders and unresolved authority references.
2. Build a bounded test case with synthetic or approved non-production data.
3. Test normal execution, stop conditions, rollback, exception handling, and evidence capture.
4. Record defects, owner, due date, retest result, and disposition.
5. Approve the effective date only after every release gate closes.

## 14. Technician Checklist

| Phase | Checklist |
|---|---|
| Before | Qualified; authorized; scope verified; dependencies healthy; before state captured; rollback ready. |
| During | Follow numbered steps; retain evidence; observe stop conditions; do not expand scope. |
| After | Verify result; complete peer review; attach evidence; close or hand off the controlling record. |

## 15. Control Assurance Review

| Finding | Consequence | Required disposition |
|---|---|---|
| Unresolved authority | The procedure can appear authoritative without a valid source. | Identify and approve the controlling authority. |
| Unmeasurable pass criteria | Execution cannot be independently verified. | Replace with objective criteria and evidence. |
| Unowned exception | Temporary risk can become permanent drift. | Assign owner, expiration, and recertification. |

<aside class="callout warning">
  <strong>Release conclusion</strong>
  <p>Replace this text with the final readiness determination, open risks, approvers, and effective-date decision.</p>
</aside>
