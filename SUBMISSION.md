# CourseLock — Consensus-Enforced Protection Against Contradictory Representations

## Reviewer description

CourseLock is a standalone GenLayer Intelligent Contract that turns prospective reliance into a reusable, fail-closed enforcement guard. A promisor and counterparty accept a frozen course; the promisor publishes an immutable representation, and the counterparty commits a specific action before submitting public evidence. Independent GenLayer leader and validator paths re-fetch and assess the evidence, then independently classify whether a later promisor position is consistent, contradictory, unrelated, or ambiguous for that same action. Deterministic state, bounded recovery and exact hashes decide whether a downstream consumer may proceed. Hardened StudioNet proofs reached BLOCKED, CLEARED, unresolved ambiguity, historical withdrawal protection and exact consumer payload/replay enforcement. No frontend, funds, or unsupported legal-finality claim.

The description is under 1,000 characters including spaces.

## Links and deployment

- GitHub: [ometere123/courselock](https://github.com/ometere123/courselock)
- Primary CourseLock: `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E`
- Consumer CourseConsumer: `0x6381F1703BFBc80ff151EB2EC3Be585aB5e3aE5C`
- Explorer base: [GenLayer Explorer](https://genlayer-explorer.vercel.app)
- Network: stable `studionet`, chain `61999`, RPC `https://studio.genlayer.com/api`
- Local CLI: repository-local `genlayer@0.39.1`; global CLI used: **NO**
- Primary deployment tx: `0xd88c8629a19c6189f9d9ece08f292c3bcb818ccaeef77e68ad4a7b003dab8674`
- Consumer deployment tx: `0x1ee27aeb7f648967b63c995ef6672e3dc3e86485acd4af9b3469b1952023c9ca`

## GenLayer-native mechanism

The reusable primitive is not a centralized AI oracle. It uses two bounded `gl.vm.run_nondet_unsafe` boundaries: independent validators re-fetch the frozen public source and materially assess completed-action support, then independently compare the frozen representation, reliance action, evidence and later position. Strict typed schemas, exact field agreement, bounded retry recovery, adversarial contradiction and clearance audits, deterministic state transitions, domain-separated hashes and a fail-closed consumer predicate turn semantic consensus into a bounded protocol decision.

## Actual proof and test counts

- 48 offline tests passed.
- 34 Direct Mode tests passed with native `VMContext.run_validator()` coverage.
- 22 structural preflight checks passed.
- 2 executable mutation invariant checks passed.
- GenVM linter `0.11.0`: both contracts validated; CourseLock 18 methods, CourseConsumer 6 methods; only informational `I200`.
- 2 hardened contracts deployed with exact source-byte parity.
- Final live lifecycle: Course 3 creation/acceptance, representation, reliance, confirmed evidence, contradiction `BLOCKED`, consistency `CLEARED`, exact `can_enforce`, stale-binding rejection; Course 1 withdrawal/closure preservation and `UNDETERMINED / MAJORITY_DISAGREE`; consumer blocked, exact success, unauthorized, payload substitution and replay receipts.

## Material limitations

The public evidence is a real immutable GitHub README commit, but it does not prove publisher ownership, wallet-to-GitHub identity, subjective reliance, physical chronology, a completed real-world action, or legal liability. Hosted DNS/redirect behavior and model availability remain runtime trust boundaries. Consensus can still agree on an incorrect natural-language interpretation. CourseLock is a participating protocol gate, not a court, legal conclusion, escrow or coercive off-chain mechanism. Direct Mode validator callbacks are native but do not reproduce full StudioNet state rollback; live receipts cover finality.

## Readiness

The code and live stable-network evidence are reviewer-ready. Final submission readiness additionally depends on the final GitHub Actions run for the release commit; no claim of green CI is made until that run is read back.
