# CourseLock — reviewer submission

## Title

CourseLock — Consensus-Enforced Protection Against Contradictory Representations

## Description

CourseLock is a standalone GenLayer Intelligent Contract that turns prospective reliance into a reusable, fail-closed enforcement guard. A promisor and counterparty accept a frozen course; the promisor publishes an immutable representation, and the counterparty commits a specific action before submitting public evidence. Independent GenLayer leader and validator paths re-fetch and assess the evidence, then independently classify whether a later promisor position is consistent, contradictory, unrelated, or ambiguous for that same action. Deterministic state and exact hashes decide whether a downstream consumer may proceed. A live StudioNet proof reached BLOCKED, CLEARED, unresolved ambiguity, withdrawal preservation, and consumer replay rejection. No frontend, funds, or unsupported legal-finality claim.

The description is under 1,000 characters including spaces.

## Links and deployment

- GitHub: [ometere123/courselock](https://github.com/ometere123/courselock)
- Primary CourseLock: `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167`
- Consumer CourseConsumer: `0xaa8a5Cd74f6A0f82A4413AF0a8ce71Bb09DcbF90`
- Explorer: [GenLayer Explorer](https://genlayer-explorer.vercel.app)
- Network: stable `studionet`, chain `61999`, RPC `https://studio.genlayer.com/api`
- Local CLI: repository-local `genlayer@0.39.1`; global CLI used: **NO**

## GenLayer-native mechanism

The reusable primitive is not a centralized AI oracle. It uses two bounded `gl.vm.run_nondet_unsafe` boundaries: independent validators re-fetch the frozen public source and materially assess completed-action support, then independently compare the frozen representation, reliance action, evidence, and later position. Strict schemas, exact field agreement, adversarial compatible-reading checks, deterministic state transitions, domain-separated hashes, and a fail-closed consumer predicate turn semantic consensus into a bounded protocol decision.

## Actual proof and test counts

- 32 offline tests passed.
- 26 Direct Mode tests passed.
- 16 structural preflight checks passed.
- 2 final contract validations passed with GenVM linter `0.11.0` (primary and consumer).
- 2 contracts deployed with exact on-chain source parity.
- Live lifecycle: 3 courses, 3 representations, 3 reliance records, 2 confirmed proof receipts, 1 rejected proof, 1 blocked position, 1 cleared position, 1 unresolved ambiguous position, and 4 finalized consumer action receipts (blocked, unauthorized, success, replay).

## Material limitations

The public evidence is a real immutable GitHub README commit, but it does not prove publisher ownership, wallet-to-GitHub identity, subjective reliance, physical chronology, or a real-world act. Hosted DNS/redirect behavior and model availability remain runtime trust boundaries. Consensus can still agree on an incorrect natural-language interpretation. CourseLock is a participating protocol gate, not a court, legal conclusion, escrow, or coercive off-chain mechanism. See [DEPLOYMENT.md](DEPLOYMENT.md) and [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for exact receipts and residual risks.

## Readiness

READY FOR REVIEW. No unresolved critical or high-severity CourseLock contract defect remains; npm installation reported dev-tooling advisories that were not auto-fixed because the CLI version is locked.
