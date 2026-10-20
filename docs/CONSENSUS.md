# CourseLock consensus and equivalence contract

This document describes the implementation in `contracts/courselock.py`, not a generic AI architecture. The deterministic contract owns authentication, ordering, bindings, storage and final status mapping. Nondeterministic callbacks only propose bounded semantic facts that must pass independent validation.

## Deterministic boundary

The contract authenticates participants with `gl.message.sender_address`, stores the accepted course scope and HTTPS namespace, assigns monotonic IDs, and records domain-separated hashes over canonical JSON. `open_course`, `accept_course`, `publish_representation`, `commit_reliance`, `open_position`, and all state transitions are deterministic. Storage mutation does not occur inside nondeterministic callbacks.

The state machine is:

```text
OFFERED -> ACTIVE -> CLOSED
ACTIVE course + ACTIVE representation -> reliance commitment
reliance -> UNPROVEN proof
UNPROVEN/RETRYABLE -> CONFIRMED / REJECTED / INCONCLUSIVE / EXHAUSTED
confirmed proof + exact hashes -> OPEN position
OPEN/RETRYABLE position -> BLOCKED / CLEARED / UNRESOLVED
```

`withdraw_representation` prevents new reliance but does not edit a prior commitment. `close_course` prevents new course operations but leaves historical records readable. `can_enforce` is a deterministic view that returns true only when the attempt is `CLEARED`, the proof is `CONFIRMED`, and the representation, commitment, position, and evidence bindings match exactly.

Assessment is restricted to the recorded promisor or counterparty. A third party cannot settle an attempt during an outage, and a finalized semantic `BLOCKED`, `CLEARED`, or `UNRESOLVED` state cannot be reassessed. Only provider/model infrastructure failures are retryable, with a maximum of three attempts and bounded history.

## Public-evidence boundary: `_proof_consensus`

The frozen inputs are the course scope, immutable representation, precommitted action, selected HTTPS URL, and exact quote.

The leader path:

1. independently calls `gl.nondet.web.render(url, mode='text')`;
2. returns a typed retryable result for a temporary fetch, empty/overlong page, malformed response, or model failure;
3. rejects an absent verbatim quote as terminal `REJECTED` before semantic classification;
4. calls `gl.nondet.exec_prompt(proof_prompt(...), response_format='json')`;
5. accepts only exactly `{status, reason}` with a valid status/retry reason.

The validator path repeats the fetch, quote check and semantic assessment independently. It does not inspect the leader’s page extract, explanation, or cached conclusion as evidence. It validates the leader’s strict shape, requires the same material status, and for retryable outcomes requires the same allowlisted infrastructure reason. A validator fetch failure does not approve a leader confirmation.

`CONFIRMED`, `REJECTED`, and semantic `INCONCLUSIVE` are terminal. `WEB_UNAVAILABLE`, `PAGE_MISSING_OR_OVERLONG`, `MALFORMED_ANALYSIS`, and `MODEL_UNAVAILABLE` are retryable only when both paths independently return the same retryable reason. The original normalized URL and exact quote are stored on the first attempt and cannot be changed on recovery. After three retryable attempts the record is `EXHAUSTED`; no later call can reopen it.

The exact quote is stored in the reliance record together with its URL, status, reason, commitment hash, bounded attempt history, and domain-separated evidence hash. The source namespace is fixed when the course is opened.

## Position boundary: `_position_consensus`

The frozen inputs are the original course scope, immutable representation, precommitted reliance action, independently confirmed evidence quote, and promisor-authored later position.

Both leader and validator independently call `position_prompt(...)`. The leader must return exactly:

```json
{
  "relation": 1,
  "same_action": true,
  "reverses_treatment": false,
  "reason": "SHORT_CODE",
  "witness": "optional concise explanation",
  "retryable": false
}
```

The relation enum is `1 CONSISTENT`, `2 CONTRADICTORY`, `3 UNRELATED`, `4 AMBIGUOUS`. A contradictory response is valid only when `same_action` and `reverses_treatment` are both true and the witness is non-empty. Retryable results are strictly limited to an ambiguous material shape with `retryable=true`, both material booleans false, an allowlisted provider reason, and an empty witness.

The validator independently compares relation, same-action, reversal, and retryability. If the proposed relation is contradictory, it invokes `attack_prompt(...)` to search for a reasonable compatible interpretation, including a hidden exception, changed actor/action/date, qualification, missing prerequisite, stale or mismatched evidence, or different scope. A counterexample or unresolved ambiguity vetoes the contradiction.

If the proposed relation is consistent, the validator invokes `clearance_attack_prompt(...)`. This symmetric audit searches for hidden qualifications, actor or counterparty substitution, reliance-action/date substitution, scope or subject substitution, selective quotation, concealed reversal, and stale evidence commitments. A material counterexample, ambiguity, malformed audit, provider failure, or leader/validator disagreement prevents the result from becoming `CLEARED`.

The contract then maps only validated material fields to state:

| Validated facts | Deterministic status |
|---|---|
| `CONTRADICTORY`, same action, reversal, no compatible reading | `BLOCKED` |
| `CONSISTENT`, same action, no reversal, no contradiction audit finding | `CLEARED` |
| retryable infrastructure result before limit | `RETRYABLE` |
| retry limit exhausted, unrelated, ambiguous, disagreement, or incomplete facts | `UNRESOLVED` or unchanged `OPEN` |

Model reasons and witnesses are descriptive outputs. They are stored for auditability but are not independently agreed word-for-word authority. `can_enforce` ignores them and checks only deterministic status and exact hashes.

## Output provenance

| Output | Source of authority |
|---|---|
| participants, scope, status, IDs, hashes and bindings | Deterministic contract state |
| quote existence in a fetched page | Deterministic check within each independent consensus path |
| proof status | Independent model classifications plus deterministic retry/terminal mapping |
| relation, same-action and reversal | Independent leader/validator classifications checked for material agreement |
| compatible/contradiction audit | Validator’s bounded independent adversarial prompt over frozen inputs |
| `BLOCKED`, `CLEARED`, `UNRESOLVED` | Deterministic mapping from validated fields |
| `can_enforce` | Deterministic exact-binding view |
| reason, witness, attempt histories | Stored explanatory/audit records, not legal findings |

The chain does not prove website ownership, publisher identity, subjective reliance, real-world identity linkage, physical chronology, completed off-chain action, or legal estoppel. The StudioNet demonstration therefore describes the GitHub README as public-content corroboration only.

## Direct Mode and runtime verification

The repository uses `genlayer-test==0.29.0`. Its native `VMContext.run_validator()` is supported and is exercised in `direct_tests` for malicious leaders, source re-fetch, malformed/extra fields, false contradiction and false consistency, positive-clearance audit vetoes, and provider failure/recovery. The Direct Mode callback helper returns whether the validator accepts the captured leader result; it is not a substitute for StudioNet consensus rollback, so live transaction receipts are separately recorded.

The pinned contract runner is `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. GenVM linter `0.11.0` validates CourseLock as 18 methods (9 view, 9 write) and CourseConsumer as 6 methods (4 view, 2 write). Both emit only informational `I200` for a newer runner; the pinned stable runner is retained.

The hardened stable StudioNet run finalized a complete Course 3 lifecycle. Its contradiction attempt read back `BLOCKED` with `same_action=true` and `reverses_treatment=true`; its compatible attempt read back `CLEARED` with `same_action=true`, `reverses_treatment=false`, and exact `can_enforce(...) == true`. A separate Course 1 assessment finalized `UNDETERMINED / MAJORITY_DISAGREE` and remained `OPEN`, demonstrating fail-closed ambiguity.
