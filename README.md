# COURSELOCK

CourseLock is a consensus-backed reliance-protection primitive that binds a promisor’s authenticated representation to a counterparty’s explicitly committed reliance, then determines whether a later enforcement position materially contradicts that representation for the same evidenced action.

It is a standalone GenLayer Intelligent Contract. It has no frontend, backend, database, Docker service, application wallet UI, funds, or legal-liability oracle. The locked deployment environment is stable `studionet`, chain `61999`, RPC `https://studio.genlayer.com/api`, with repository-local `genlayer@0.39.1`.

## Hardened release

The hardened contracts were deployed to stable StudioNet and their source bytes were retrieved from the chain with `gen_getContractCode`, decoded, SHA-256 hashed, and compared byte-for-byte with the local files.

- CourseLock: `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E`
- CourseConsumer: `0x6381F1703BFBc80ff151EB2EC3Be585aB5e3aE5C`
- Explorer base: [GenLayer Explorer](https://genlayer-explorer.vercel.app)
- CourseLock source SHA-256: `afd51b388aafd35c97f8aaee6a4edaf4a9667bd5f2394a6b7fab46c479fcfea8`
- CourseConsumer source SHA-256: `57ac638294a4661340304099848bba6c7ee1fbca9142c038ffc52683d8228cd6`

The deployment transaction hashes and finalized readbacks are recorded in [DEPLOYMENT.md](DEPLOYMENT.md). The earlier baseline deployment remains preserved there as historical evidence and is not evidence for the hardened source.

The live evidence uses an immutable README at commit `198b6089f1a10db196d76289aea58e12824ab74a`. Validators independently retrieved the selected raw URL and found the exact quote, but that public page does not prove publisher ownership, wallet-to-GitHub identity, subjective reliance, physical chronology, real-world action completion, or legal liability. Those are explicit protocol limitations.

## Why this primitive exists

A deterministic contract can authenticate who called a method and compare hashes, but it cannot reliably decide whether natural-language evidence supports a completed action or whether a qualified later position materially reverses an earlier treatment. A centralized AI judgment is also a single subjective failure point. CourseLock separates authenticated state transitions from two bounded independent-consensus boundaries.

```text
promisor                                      counterparty
  open_course(counterparty, scope, HTTPS namespace)
                                               accept_course(course_id)
  publish_representation(text)
                                               commit_reliance(action, reason, rep_hash)
                                               prove_action(public URL, exact quote)
  open_position(later position, commitment_hash, evidence_hash)
  assess_position(attempt_id)

  CONTRADICTORY + same action + material reversal -> BLOCKED
  CONSISTENT + same action + no reversal          -> CLEARED
  AMBIGUOUS / UNRELATED / unsupported             -> UNRESOLVED or no clearance
```

`BLOCKED` is a protocol protection result, not a declaration of legal liability. `CLEARED` is a scoped positive predicate for one exact attempt; it is not blanket authorization.

## Main API

| Method | Authenticated caller | Effect |
|---|---|---|
| `open_course(counterparty, scope, source_prefix)` | Promisor | Creates a unique course and freezes its counterparty, scope, and HTTPS evidence namespace. |
| `accept_course(course_id)` | Designated counterparty | Activates the offered course. |
| `publish_representation(course_id, text)` | Promisor | Records an immutable representation and domain-separated hash. |
| `withdraw_representation(rep_id)` | Promisor | Stops new reliance without erasing prior reliance. |
| `commit_reliance(rep_id, action, reason, expected_representation_hash)` | Counterparty | Records a specific prospective reliance binding. |
| `prove_action(reliance_id, evidence_url, evidence_quote)` | Counterparty | Independently fetches and assesses public evidence. Transient infrastructure failures are retryable at most three times with the original URL and quote frozen. |
| `open_position(reliance_id, text, expected_commitment_hash, expected_evidence_hash)` | Promisor | Freezes a later enforcement position against exact prior bindings. |
| `assess_position(attempt_id)` | Promisor or counterparty | Independently classifies the frozen representation, action, evidence, and position. Transient model failures are retryable at most three times; third-party assessment is rejected. |
| `can_enforce(attempt_id, rep_hash, reliance_hash, position_hash)` | View | Returns true only for an exact, completed `CLEARED` decision with confirmed evidence. |
| `is_protected(attempt_id)` | View | Returns true only for a completed, materially contradictory protected attempt. |
| `get_course`, `get_representation`, `get_reliance`, `get_attempt` | Anyone | Read immutable records, hashes, statuses, and bounded history. |

The consumer adds `commit_action(attempt_id, rep_hash, commitment_hash, position_hash, payload)` and `execute(attempt_id, rep_hash, commitment_hash, position_hash, payload, payload_hash, action_id)`. The payload commitment is domain-separated and binds the exact CourseLock attempt and all three hashes. The executor must commit the intent before executing it, and each intent and action ID is one-time.

Stable status integers are exposed by `get_status_dictionary`: courses `OFFERED=1, ACTIVE=2, CLOSED=3`; representations `ACTIVE=1, WITHDRAWN=2`; proofs `UNPROVEN=0, CONFIRMED=1, REJECTED=2, INCONCLUSIVE=3, RETRYABLE=4, EXHAUSTED=5`; relations `CONSISTENT=1, CONTRADICTORY=2, UNRELATED=3, AMBIGUOUS=4`; attempts `OPEN=0, CLEARED=1, BLOCKED=2, UNRESOLVED=3, RETRYABLE=4`.

The consumer gate fails closed for unknown, unproven, rejected, inconclusive, retryable, exhausted, pending, stale, ambiguous, unrelated, blocked, or hash-mismatched states. Only exact positive `can_enforce(...) == true` can pass.

## Consensus security

The proof boundary in `_proof_consensus` has explicit leader and validator paths. Each path independently retrieves the frozen URL with `gl.nondet.web.render`, rejects an absent quote before semantic classification, and runs a strict JSON semantic check. The validator never trusts the leader’s page extract, reason, or model conclusion. `CONFIRMED`, `REJECTED`, and semantic `INCONCLUSIVE` remain terminal; web/model infrastructure failures are represented separately as bounded `RETRYABLE` attempts and become `EXHAUSTED` after the limit.

The position boundary in `_position_consensus` independently classifies `relation`, `same_action`, and `reverses_treatment`. The validator checks strict types/enums and, for a claimed contradiction, performs a bounded compatible-reading audit for exceptions, changed actors/actions/dates, qualifications, evidence and scope. A claimed `CONSISTENT` result receives the symmetric contradiction-seeking clearance audit before it can become `CLEARED`. A counterexample, ambiguity, malformed result, provider failure, or leader/validator disagreement cannot create affirmative clearance.

URL validation is fail-closed for non-HTTPS URLs, controls, backslashes, query/fragment/percent encoding, userinfo, ports, malformed hostnames, IP-like or local/private wrapper names, and path traversal. This is namespace hardening, not proof of real-world source ownership; redirects, DNS resolution, source freshness, and hosted egress policy remain explicit trust assumptions.

## Verification

The final local results are:

- `python -m pytest tests -q` → **48 passed**.
- `python scripts/preflight.py` → **22 checks passed**.
- `python scripts/source_consistency.py` → passed.
- `python -m py_compile contracts/courselock.py contracts/course_consumer.py` → passed.
- Direct Mode with `genlayer-test==0.29.0` → **34 passed** using the Windows `gltest.exe direct_tests -v -s` command.
- Native `VMContext.run_validator()` coverage is included in Direct Mode for malicious leaders, independent evidence refetch, malformed results, false contradiction/consistency, positive clearance audits, and provider recovery. The harness returns validator agreement but does not reproduce StudioNet’s state rollback on its own; live StudioNet receipts are used for actual consensus finality.
- GenVM linter `0.11.0` → both contracts validated. CourseLock: 18 methods (9 view, 9 write); CourseConsumer: 6 methods (4 view, 2 write); both report only informational `I200` for a newer runner.
- Stable RPC guard → `eth_chainId = 0xf22f` (`61999`) at the required RPC.
- Local CLI → repository-local `genlayer --version` is `0.39.1`; the global CLI was not used.
- `npm audit --omit=dev --audit-level=high` → zero production/high/critical findings. The full dependency tree retains two moderate development-tool advisories documented in the threat model.
- Executable mutation checks cover removal of terminal proof protection and third-party assessment authorization; each mutant changes a relevant regression outcome.

The final StudioNet evidence includes a fully captured Course 3 lifecycle: finalized creation, acceptance, representation, reliance, confirmed evidence, contradiction blocked, consistent position cleared, exact `can_enforce` readbacks, stale-binding rejection, and historical withdrawal/closure checks on Course 1. CourseConsumer was exercised with blocked, exact success, unauthorized, payload-substitution, and replay transactions.

Run reproducible local checks with:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/preflight.py
python scripts/source_consistency.py
```

For stable-network work, use `npm ci`, verify `0.39.1` with the repository-local executable, run `node scripts/assert_studionet.mjs`, and use `npm run deploy:guarded`. On Windows the exact binary is `.\node_modules\.bin\genlayer.cmd`; never invoke the globally installed `0.40.0rc2`. No deployment secret is committed or printed.

See [DEPLOYMENT.md](DEPLOYMENT.md) for actual transaction evidence, [docs/CONSENSUS.md](docs/CONSENSUS.md) for execution paths, [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for residual risks, [docs/INTEGRATION.md](docs/INTEGRATION.md) for the consumer contract, [docs/TEST_PLAN.md](docs/TEST_PLAN.md) for coverage, and [SUBMISSION.md](SUBMISSION.md) for reviewer-facing material.

MIT licence. No frontend, backend, Docker, database, or application wallet integration.
