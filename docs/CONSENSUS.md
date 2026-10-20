# Consensus and equivalence contract

This document describes the implementation in `contracts/courselock.py`, not a generic AI architecture.

## Deterministic boundary

The contract authenticates participants with `gl.message.sender_address`, stores the accepted course scope and HTTPS namespace, assigns monotonic IDs, and records domain-separated hashes over canonical JSON. `open_course`, `accept_course`, `publish_representation`, `commit_reliance`, `open_position`, and all status transitions are deterministic. Storage and state mutation do not occur inside nondeterministic callbacks.

The relevant state machine is:

```text
OFFERED -> ACTIVE -> CLOSED
ACTIVE course + ACTIVE representation -> reliance commitment
reliance -> one proof decision
confirmed proof + exact hashes -> OPEN position
OPEN position -> BLOCKED / CLEARED / UNRESOLVED
```

`withdraw_representation` prevents new reliance but does not edit a prior commitment. `close_course` prevents new course operations but leaves historical records readable. `can_enforce` is a deterministic view that returns true only when the attempt is `CLEARED`, the proof is `CONFIRMED`, and the representation, commitment, position, and evidence bindings match exactly.

## Public-evidence boundary: `_proof_consensus`

The frozen inputs are the course scope, representation text, precommitted action, selected HTTPS URL, and exact quote.

The leader callback:

1. calls `gl.nondet.web.render(url, mode='text')`;
2. fails closed for unavailable/empty/overlong pages;
3. rejects an absent verbatim quote before semantic classification;
4. calls `gl.nondet.exec_prompt(proof_prompt(...), response_format='json')`;
5. accepts only the exact fields `status` and `reason`, with status `CONFIRMED`, `REJECTED`, or `INCONCLUSIVE`.

The validator callback independently performs the same fetch, quote check, and semantic assessment. It does not inspect the leader’s page extract, reason, or model conclusion as evidence. It accepts the nondeterministic result only when its own material `status` matches the leader’s strict result. Unavailability, malformed output, missing quote, or disagreement cannot produce confirmed proof.

The exact quote is stored in the reliance record together with its URL, status, reason, commitment hash, and a domain-separated evidence hash. The source namespace is fixed when the course is opened.

## Contradiction boundary: `_position_consensus`

The frozen inputs are the original course scope, immutable representation, precommitted reliance action, independently confirmed evidence quote, and promisor-authored later position.

Both leader and validator independently call `position_prompt(...)` and must return the strict fields:

```json
{
  "relation": 1,
  "same_action": true,
  "reverses_treatment": false,
  "reason": "SHORT_CODE",
  "witness": "optional concise old-vs-new explanation"
}
```

The enum is `1 CONSISTENT`, `2 CONTRADICTORY`, `3 UNRELATED`, `4 AMBIGUOUS`. A contradictory response is valid only if `same_action` and `reverses_treatment` are both true and the witness is non-empty. The validator independently compares the three material fields. If the proposed relation is contradictory, it also invokes `attack_prompt(...)` to look for a bounded compatible interpretation, including a hidden exception, changed actor/action/date, qualification, missing prerequisite, or different scope. A counterexample or ambiguity rejects the contradiction result.

The validator does not merely check JSON shape or repeat the leader’s text. It recomputes the material classification from the frozen inputs. A disagreement causes `run_nondet_unsafe` validation to fail; the contract never turns that into clearance.

## Output provenance

| Output | Source of authority |
|---|---|
| participant, scope, status, IDs, hashes, bindings | Deterministic contract state |
| quote existence in independently fetched page | Deterministic check within each consensus path |
| proof status | Independent model classification plus deterministic status assignment |
| relation, same-action, reversal | Independent model classifications checked for agreement |
| reason and witness | Explanatory model output; not independently agreed word-for-word evidence |
| `BLOCKED`, `CLEARED`, `UNRESOLVED` | Deterministic mapping from validated enum fields |
| `can_enforce` | Deterministic exact-binding view |

The chain does not prove website ownership, subjective reliance, real-world identity linkage, physical chronology, or legal estoppel. The live demonstration therefore describes its GitHub README evidence as public-content corroboration only.

## Runtime verification

The pinned headers use `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`. GenVM linter `0.11.0` validated the final primary contract (16 methods, 7 views, 9 writes) and consumer (4 methods, 3 views, 1 write, 1 constructor). The linter emitted only informational `I200` for a newer runner; changing the pinned stable-runtime header would have been an unjustified migration.

The live StudioNet receipts independently exercised the proof and position paths. Course 1 produced `BLOCKED` with `DIRECT_NEGATION_SAME_ACTION`; Course 2 produced `CLEARED` with `NO_CONTRADICTION`; a materially ambiguous position finalized without a state transition and remained unable to pass `can_enforce`.
