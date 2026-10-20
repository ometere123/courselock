# COURSELOCK

CourseLock is a consensus-backed reliance-protection primitive that binds a promisor’s authenticated representation to a counterparty’s explicitly committed reliance, then determines whether a later enforcement position materially contradicts that representation for the same evidenced action.

It is a standalone GenLayer Intelligent Contract. It has no frontend, backend, database, Docker service, application wallet UI, funds, or legal-liability oracle. The deployed network is stable `studionet`, chain `61999`, RPC `https://studio.genlayer.com/api`; the repository-local CLI is `genlayer@0.39.1`.

## Release status

The primary CourseLock IC and the optional CourseConsumer IC were deployed and exercised on stable StudioNet. The immutable source returned by the chain matched the local files byte-for-byte.

- Primary: `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167`
- Consumer: `0xaa8a5Cd74f6A0f82A4413AF0a8ce71Bb09DcbF90`
- Explorer: [GenLayer Explorer](https://genlayer-explorer.vercel.app)
- Primary source SHA-256: `c5d06e1de41d0fc7a0982575f66fe293151b8afd90078550e2da9cfe0b1b537a`
- Consumer source SHA-256: `62ffdf651e1e5bd6b0808776e6c0afab3cc4c23424877e56a646988d5e428257`

The live evidence uses an immutable README at commit `198b6089f1a10db196d76289aea58e12824ab74a`. That page is real public content and its quote was independently retrieved by validators, but it is not proof that a wallet holder performed an off-chain act or that the publisher owns the wallet. This limitation is intentional and documented.

## Why this primitive exists

A deterministic contract can authenticate who called a method and compare hashes, but it cannot reliably decide whether natural-language evidence supports a completed action or whether a qualified later position materially reverses an earlier treatment. A centralized AI judgment is also a single subjective failure point. CourseLock separates the authenticated state transitions from two bounded independent-consensus boundaries.

```text
promisor                         counterparty
  open_course(counterparty, scope, HTTPS namespace)
                                  accept_course(course_id)
  publish_representation(text)
                                  commit_reliance(action, reason, rep_hash)
                                  prove_action(public URL, exact quote)
  open_position(later position, commitment_hash, evidence_hash)
  assess_position(attempt_id)

  CONTRADICTORY + same action + material reversal -> BLOCKED
  CONSISTENT + same action + no reversal       -> CLEARED
  AMBIGUOUS / UNRELATED / missing proof        -> UNRESOLVED or no clearance
```

`BLOCKED` is a protocol protection result, not a declaration of legal liability. `CLEARED` is a scoped positive predicate for consumers; it is not a blanket authorization.

## Main API

| Method | Authenticated caller | Effect |
|---|---|---|
| `open_course(counterparty, scope, source_prefix)` | Promisor | Creates a unique course and freezes its counterparty, scope, and HTTPS evidence namespace. |
| `accept_course(course_id)` | Designated counterparty | Activates the offered course. |
| `publish_representation(course_id, text)` | Promisor | Records an immutable representation and domain-separated hash. |
| `withdraw_representation(rep_id)` | Promisor | Stops new reliance without erasing prior reliance. |
| `commit_reliance(rep_id, action, reason, expected_representation_hash)` | Counterparty | Records a specific prospective reliance binding. |
| `prove_action(reliance_id, evidence_url, evidence_quote)` | Counterparty | Independently fetches and semantically assesses public evidence once. |
| `open_position(reliance_id, text, expected_commitment_hash, expected_evidence_hash)` | Promisor | Freezes a later enforcement position against exact prior bindings. |
| `assess_position(attempt_id)` | Any caller | Independently compares the frozen representation, action, evidence, and position. |
| `can_enforce(attempt_id, rep_hash, reliance_hash, position_hash)` | View | Returns true only for an exact, completed `CLEARED` decision. |
| `is_protected(attempt_id)` | View | Returns true only for a completed, materially contradictory protected attempt. |
| `get_course`, `get_representation`, `get_reliance`, `get_attempt` | Anyone | Read immutable records and hashes. |

Statuses are stable machine-readable integers: `Course OFFERED=1, ACTIVE=2, CLOSED=3`; `Representation ACTIVE=1, WITHDRAWN=2`; `Proof UNPROVEN=0, CONFIRMED=1, REJECTED=2, INCONCLUSIVE=3`; `Position OPEN=0, CLEARED=1, BLOCKED=2, UNRESOLVED=3`.

The consumer gate fails closed for unknown, unproven, rejected, inconclusive, pending, stale, ambiguous, unrelated, blocked, or hash-mismatched states. Only an exact positive `can_enforce(...) == true` can pass.

## Consensus security

The proof boundary in `_proof_consensus` runs `gl.nondet.web.render` and a semantic prompt separately in the leader and validator paths. Both paths require strict `{status, reason}` schemas, independently retrieve the URL, verify the exact quote, and compare the material proof status. A leader-provided extract is never accepted as validator evidence.

The position boundary in `_position_consensus` independently classifies `relation`, `same_action`, and `reverses_treatment`. The validator checks strict types/enums and, for a claimed contradiction, performs a bounded compatible-reading audit for exceptions, changed actors/actions, qualifications, and alternative scope. The deterministic contract sets the final status; model explanations and witnesses are descriptive, not authority.

URL validation is fail-closed for non-HTTPS URLs, controls, backslashes, query/fragment/percent encoding, userinfo, ports, malformed hostnames, IP-like or local/private wrapper names, and path traversal. This is namespace hardening, not proof of real-world source ownership; redirect and hosted DNS policy remain explicit trust assumptions.

## Verification

Final local results:

- `python -m pytest tests -q`: 32 passed.
- `python scripts/preflight.py`: 16 checks passed.
- GenVM Direct Mode: 26 passed with `genlayer-test==0.29.0`.
- GenVM linter: `genvm-linter==0.11.0`; primary and consumer validation passed. The only reported item was informational `I200` about a newer runner; the pinned contract runner was retained.
- Stable RPC guard: `eth_chainId = 0xf22f` (`61999`) at the required RPC.
- Live proof: blocked contradiction, cleared consistent position, ambiguous no-clearance, invalid evidence, withdrawal/closure preservation, and consumer block/success/replay were all exercised with finalized StudioNet receipts.

Run the reproducible offline checks with:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/preflight.py
```

For stable-network work, install dependencies with `npm ci` when the lockfile is present, verify `0.39.1` with the repository-local executable, run `node scripts/assert_studionet.mjs`, and use `npm run deploy:guarded`. On Windows the exact binary is `.\node_modules\.bin\genlayer.cmd`; never invoke the globally installed `0.40.0rc2`.

See [DEPLOYMENT.md](DEPLOYMENT.md) for actual transaction evidence, [docs/CONSENSUS.md](docs/CONSENSUS.md) for execution paths, [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for residual risks, [docs/INTEGRATION.md](docs/INTEGRATION.md) for the consumer contract, [docs/TEST_PLAN.md](docs/TEST_PLAN.md) for coverage, and [SUBMISSION.md](SUBMISSION.md) for reviewer-facing material.

MIT licence. No frontend, backend, Docker, database, or application wallet integration.
