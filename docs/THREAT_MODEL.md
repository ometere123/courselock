# CourseLock threat model

CourseLock protects authenticated course state, immutable representation hashes, prospective reliance commitments, evidence receipts, semantic position decisions, and a downstream consumer’s exact one-time gate. It does not protect off-chain money, force a party to participate, prove legal liability, prove a wallet’s real-world identity, or establish ownership of a public website.

## Actors and trust boundaries

- Promisor: creates the course, publishes/withdraws its own representation, and submits later positions.
- Designated counterparty: explicitly accepts, commits its own prospective reliance, and submits its own evidence receipt.
- Unauthorized wallet: must not impersonate either participant or the consumer executor.
- Malicious leader: may fabricate evidence, omit qualifications, truncate context, swap identities, or lie about a semantic result.
- Malicious validator: may disagree or return malformed output; consensus must fail closed.
- Public source/publisher: may be false, incomplete, mutable, or unrelated to a wallet.
- Third-party assessor: may intentionally call assessment during an outage to try to settle another party’s position.
- Hosted GenLayer web/model providers: are runtime availability and retrieval boundaries, not sources of legal truth.
- Consumer integrator: must pin the final CourseLock address, exact attempt bindings, payload and executor rules.

## Protected invariants

1. Only the recorded promisor publishes a representation or opens a position.
2. Only the designated counterparty accepts the course, commits reliance, or submits proof.
3. Course scope, participants and source namespace are immutable after creation; IDs are monotonic.
4. A reliance commitment precedes evidence assessment and any later enforcement position.
5. The exact representation, commitment, evidence and position hashes remain bound across all later calls.
6. Withdrawal and closure stop new operations without erasing earlier commitments, evidence or attempts.
7. Only completed exact `CLEARED` state can satisfy `can_enforce`; ambiguity and infrastructure failure never clear.
8. A consumer action intent binds an exact attempt, three exact CourseLock hashes and a domain-separated payload hash; it is one-time and executor-authenticated.

## Attack classes and mitigations

| Attack | Mitigation / residual risk |
|---|---|
| Forged promisor representation or position | `publish_representation` and `open_position` require the recorded promisor sender. Domain-separated hashes bind course, author, representation, reliance, evidence and position. |
| Counterparty impersonation | Acceptance, reliance and evidence submission require the designated counterparty sender. |
| Third-party assessment griefing | `assess_position` is restricted to the promisor or counterparty. Transient provider failures produce a bounded retryable state rather than a terminal semantic decision. |
| Course owner bypass after reliance | Scope and participant identity are frozen. Withdrawal and closure stop future operations but do not erase prior commitments or historical attempts. |
| Reliance committed after withdrawal | `commit_reliance` requires an active course and active representation. Existing reliance remains readable and settleable under its original bindings. |
| Stale representation, commitment or evidence substitution | Expected representation, commitment and evidence hashes are checked at each later boundary. A stale live `open_position` finalized with `STALE_BINDING`. |
| Fabricated quote | Both leader and validator independently fetch the selected URL and check exact quote occurrence before semantic classification. Quote presence is necessary, not sufficient. |
| Misleading surrounding context | Prompts require full-page/context review; the validator independently classifies action support. A public page can still omit or misstate facts, which remains a provenance risk. |
| Prompt injection in page, quote, caller field or position | Delimited values are untrusted data; instructions inside them are not followed. Strict schemas and independent material assessment prevent prose from changing deterministic state directly. |
| Namespace confusion / SSRF-style URL | URL normalization rejects non-HTTPS, controls, backslashes, query/fragment/percent encoding, userinfo, ports, malformed hostnames, IP-like/numeric/wrapper names, local/private suffixes and traversal. Redirect and DNS policy remain hosted-runtime trust assumptions. |
| Malicious leader fabricates contradiction | Validator independently classifies relation, same action and reversal, then runs a bounded compatible-reading audit for exceptions, changed actors/actions/dates, qualifications and scope. |
| Malicious leader fabricates clearance | Validator independently classifies the position and runs a symmetric contradiction-seeking clearance audit. Any material counterexample, ambiguity, malformed result, or disagreement withholds clearance. |
| Temporary web/model outage | Only allowlisted infrastructure failures are `RETRYABLE`; original URL/quote or position content cannot change; attempts are capped at three and histories are preserved. Semantic `CONFIRMED`, `REJECTED`, `INCONCLUSIVE`, `BLOCKED`, `CLEARED` and `UNRESOLVED` decisions are terminal. |
| Retry substitution or exhaustion grief | Recovery is authorized only for the correct actor, exact frozen inputs and remaining allowance. Third parties cannot consume assessment recovery; an exhausted record cannot reopen. |
| False clearance | `can_enforce` is deterministic and requires `CLEARED`, `CONFIRMED`, exact representation/commitment/position/evidence bindings. Unknown, pending, retryable, exhausted, unresolved, ambiguous, unrelated, rejected or malformed states do not clear. |
| Consumer stale/unrelated receipt | `CourseConsumer` calls typed `can_enforce` with the exact attempt and three hashes, then compares the stored intent bindings and recomputed domain-separated payload hash. |
| Consumer payload substitution | A payload is committed before execution; changing payload, payload hash or any bound hash finalizes with an error and does not increment the counter. |
| Consumer replay | A 64-character lowercase-hex action ID is stored once, and each attempt intent has an executed flag. Exact replay and alternate-ID reuse of an executed intent are rejected. |
| Consumer unauthorized use | The constructor records `executor`; every write requires that sender. |
| State/storage spam | Text, page and URL lengths are bounded; per-course, per-representation, per-reliance and per-reliance-attempt counts are capped. Global transaction spam remains a chain-level concern. |
| Reentrancy / fund theft | No funds, token transfers, callbacks, administrator override, upgrade path or external writes exist. The consumer performs only a typed view before its own local write. |

## Assumptions

1. StudioNet validators execute the pinned source under the declared GenVM runner and the consensus mechanism supplies independent validator paths.
2. `gl.nondet.web.render` can independently retrieve the same public source often enough for an affirmative result; source mutation can instead produce rejection, disagreement or retryable failure.
3. Participants control their signing keys. CourseLock authenticates wallet addresses, not names, organizations or legal identity.
4. Consumer integrators verify the deployed primary address and pass the exact binding tuple and payload. A consumer that ignores `can_enforce` is outside this protocol’s guarantees.
5. Public evidence namespaces are mutually accepted URL scopes, not cryptographic publisher identity proofs.
6. Natural-language classifiers and public sources can still be wrong even when validators agree; the audits reduce but do not eliminate semantic error.

## Residual risks and accepted limitations

- The live README demonstration proves only that a quote was independently retrievable from a fixed public GitHub raw commit. It does not prove website ownership, wallet-to-person identity, subjective reliance, a physical/off-chain act, or legal liability.
- Redirect behavior, DNS resolution, content freshness, and provider egress controls are hosted-runtime policies. The contract rejects unsafe URL spellings but cannot authenticate DNS ownership or every redirect target.
- A promisor can refuse to open a position or act off-chain. CourseLock is a participating protocol gate, not a coercive mechanism or court.
- Provider outages can leave a correct attempt retryable or exhausted; recovery is intentionally bounded and never upgrades an uncertain semantic result to confirmation.
- Direct Mode’s `run_validator()` exercises the native callback interface but does not itself reproduce the full StudioNet state rollback. Finality and state-preservation claims are based on live receipts/readbacks, not simulation.
- The npm dependency tree retains two moderate nested `dockerode`/`uuid` development-tool advisories. Production, high and critical audit findings are zero; the Python deployed contracts have no runtime dependency on npm packages.
