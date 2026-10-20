# COURSELOCK

**Pre-action reliance becomes an immutable, consensus-verifiable enforcement boundary.** A promisor cannot obtain clearance in an opt-in consumer contract for a materially contradictory later position against a counterparty's already-committed, publicly corroborated reliance action.

**Standalone GenLayer Intelligent Contract — no frontend, no backend — stable `studionet` / chain `61999` — repo-local CLI `genlayer@0.39.1`.**

> [!IMPORTANT]
> **Source code is built; live StudioNet deployment and source-matched finalized lifecycle remain pending.** Do not submit this repository as deployed until the Codex handoff and `DEPLOYMENT.md` acceptance checklist are complete. This project does not claim to be a legal estoppel adjudicator, to verify subjective intentions, or to reverse off-chain actions.

## Why this primitive exists

Conventional checks compare today's terms with today's action. **CourseLock makes a previously authenticated representation and a counterparty's *pre-action* commitment part of the required enforcement history.** The same later position can be compatible in an unrelated transaction and **blocked for the action that demonstrably depended on the earlier representation**. This is a new stateful permission boundary, not an ordinary text comparison.

```text
Alice (promisor)                    Bob (relying party)
  open_course(Bob, frozen_scope, pre-agreed evidence namespace)
                                    accept_course(course_id)
  publish_representation("Friday submissions are timely")
                                    commit_reliance("Submit item 41 Thursday", ...)
                                    [performs the real-world act]
                                    prove_action(source-backed receipt + exact quote)
  open_position("Thursday is late; deadline was Wednesday", ...)
                     anyone assesses position with GenLayer consensus
  status BLOCKED ───────────────────> downstream consumer refuses enforcement

  open_position("Thursday is timely", ...)
  status CLEARED ───────────────────> downstream consumer may execute, once
```

**The original representation is wallet-authored on-chain by the promisor.** The reliance commitment is wallet-authored by the counterparty *before evidence is submitted*; the proof URL must belong to the exact HTTPS namespace both parties accepted. Evidence is fetched independently by GenLayer validators. The later position is authenticated by the promisor, not inferred from a third-party page. These are four different trust claims and the code never conflates them.

## Main API

| Method | Caller | Consequence |
|---|---|---|
| `open_course(counterparty, scope, source_prefix)` | Promisor | Freeze counterparty, course scope and HTTPS evidence namespace |
| `accept_course(course_id)` | Counterparty | Activates mutually agreed course |
| `publish_representation(course_id, text)` | Promisor | Immutable representation/hash |
| `withdraw_representation(rep_id)` | Promisor | Stops *new* reliance, doesn't invalidate existing reliance |
| `commit_reliance(rep_id, action, reason, expected_representation_hash)` | Counterparty | Immutable pre-action intent/explicit reliance binding |
| `prove_action(reliance_id, evidence_url, evidence_quote)` | Counterparty | Source-backed GenLayer consensus, one immutable result |
| `open_position(reliance_id, text, expected_commitment_hash, expected_evidence_hash)` | Promisor | Freeze later attempted enforcement, currently no clearance |
| `assess_position(attempt_id)` | Anyone | Independent semantic comparison; adversarial validator audit on contradiction |
| `close_course(course_id)` | Either party | Prevents *new* representations/reliance, preserves prior records |
| `can_enforce(attempt_id, rep_hash, reliance_hash, position_hash)` | Consumer view | Exact binding and positive clearance only |
| `is_protected(attempt_id)` | Consumer view | True only for finalized contradiction status |
| `get_course`, `get_representation`, `get_reliance`, `get_attempt` | Anyone | Immutable record inspection |

### Statuses

`Course: OFFERED=1, ACTIVE=2, CLOSED=3`. `Representation: ACTIVE=1, WITHDRAWN=2`. `Proof: UNPROVEN=0, CONFIRMED=1, REJECTED=2, INCONCLUSIVE=3`. `Position: OPEN=0, CLEARED=1, BLOCKED=2, UNRESOLVED=3`.

**Fail-closed:** unknown, unproven, rejected, ambiguous, unrelated, pending, stale, or mismatched hash ⇒ `can_enforce = False`. Only a **scoped, positively consistent** position is `CLEARED`. A `BLOCKED` attempt is a protected reliance case; do not interpret it as universal legal liability.

## Why GenLayer consensus matters

The relevant questions are not deterministic string equivalences: *Does a public receipt materially corroborate the precommitted specific act?* And, *Does the promisor's new position materially deny the treatment promised for that exact act?* These require contextual semantics (conditions, time, actors, exceptions, and scope) that syntax rules cannot robustly decide.

There are **two bounded `gl.vm.run_nondet_unsafe`** consensus boundaries:

1. **Proof:** leader fetches the exact agreed-namespace URL, checks a verbatim quote is present in the fetched page, then classifies specific-action support; validators **independently re-fetch and assess** the action, matching the material proof status, not just output formatting.
2. **Position:** leader compares immutable representation, intent, corroborated quote, and newly authenticated promisor position. Validators **independently classify** material relation, same-action applicability and reversal. Any claimed contradiction additionally triggers an **adversarial alternative-interpretation check**. If either validator check disagrees, leader outcome is not accepted by consensus.

LLM-generated explanations and witnesses are **leader-reported, not independently agreed evidence**; the status and binding fields are the consensus material. No AI chooses financial penalties, modifies representations, chooses parties, creates authority, changes the accepted namespace or executes off-chain operations.

## Core invariants

- Both parties must consent to the frozen course; only the promisor can issue its representation and later position, only the counterparty can commit reliance and submit action evidence.
- The representation is immutable. Withdrawal and closure only prevent **future** reliance; neither retroactively alters recorded reliance.
- A claim of reliance is **logged before a later receipt can be submitted**, and the exact original representation hash is a required call parameter. This is **not** an external chronology proof; genuine physical act timing needs source evidence and independent assessment.
- Action evidence is sourced from an HTTPS prefix fixed at course creation and accepted by the counterparty; the quote must be verbatim in the fetched page. Source text is hostile input, never instructions to the validator.
- Source unavailability, oversized content and absence of the quote do not produce confirmed action proof. Provenance is limited to the **mutually approved namespace**, not a proof of website ownership.
- Attempts reference the exact frozen commitment and evidence hashes, can only be authored by the promisor, cannot change after creation, and remain pending until independently assessed.
- No final clearance is given to ambiguous or unrelated enforcement, or to a contradiction. Only a consensus-confirmed scoped consistent position passes `can_enforce`.
- The consumer checks the exact triple `(representation_hash, commitment_hash, position_hash)` and enforces a **one-time action ID** to prevent replay.
- Storage growth is bounded per course, representation and reliance. No administrator, upgrade bypass, arbitrary network selection, or automatic money transfers.

## Quick verification

```sh
python -m pytest tests -q
python scripts/preflight.py

# GenVM Direct Mode (on your developer workstation; requires Python 3.12+)
python -m pip install -r requirements-dev.txt
gltest direct_tests/test_courselock_direct.py -v -s
```

**Current locally verified:** 32 offline-mock tests passed; 16 structural preflight checks passed. Direct Mode and finalized live consensus are **not yet executed/verified**. The initially included Direct Mode suite is a smoke suite; full two-wallet Direct Mode adversarial lifecycle is an explicit Codex completion requirement. See `docs/TEST_PLAN.md`.

### Stable StudioNet 61999 (never the preview)

```sh
npm install
./node_modules/.bin/genlayer --version  # exactly 0.39.1
node scripts/assert_studionet.mjs       # RPC must prove 61999
npm run deploy:guarded                 # confirmation gate, deploy primary
```

On Windows, use `npx --no-install genlayer --version` and `npm run deploy:guarded`. Neither command is allowed to invoke globally installed `0.40.0rc2`. **Don't substitute the preview environment or its chain ID.**

The guarded deploy script uses `https://studio.genlayer.com/api` explicitly. A separate optional `CourseConsumer` needs constructor `course_lock_address` from the **finalized** primary deployment. The primary IC alone is the standalone submission. Full setup, source parity and evidence checklist: [DEPLOYMENT.md](DEPLOYMENT.md).

## Architecture documentation

- [Consensus/equivalence specification](docs/CONSENSUS.md)
- [Security threat model](docs/THREAT_MODEL.md)
- [Integration and proof acceptance contract](docs/INTEGRATION.md)
- [Test matrix and remaining test gates](docs/TEST_PLAN.md)
- [Lifecycle walkthrough](examples/delivery_reliance.md)
- [Submission checklist](SUBMISSION.md)
- [Pending deployment/source parity](DEPLOYMENT.md)

### Sources

- [GenLayer Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [GenLayer non-determinism](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism)
- [GenLayer stable hosted network configuration](https://docs.genlayer.com/developers/intelligent-contracts/deploying/network-configuration)
- [CLI 0.39.1 reference](https://docs.genlayer.com/api-references/genlayer-cli)

MIT licence. No frontend, dashboard, backend, database, wallet UI or paid external service.
