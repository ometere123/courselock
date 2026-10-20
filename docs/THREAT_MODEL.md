# CourseLock threat model

CourseLock protects authenticated course state, representation hashes, prospective reliance commitments, evidence receipts, semantic position decisions, and the downstream consumer’s exact one-time gate. It does not protect off-chain money, force a party to participate, prove legal liability, or prove a wallet’s real-world identity.

## Actors and trust boundaries

- Promisor: may create an accepted course, publish/withdraw its own representations, and submit later positions.
- Designated counterparty: must explicitly accept, commit its own reliance, and submit its own evidence receipt.
- Unauthorized wallet: must not impersonate either participant.
- Malicious leader: may fabricate evidence, omit qualifications, truncate context, swap identities, or lie about a semantic result.
- Malicious validator: may disagree or return malformed output; consensus must fail closed.
- Public source/publisher: may be false, incomplete, mutable, or unrelated to a wallet.
- Consumer: may be correct or incorrectly integrated; it must pin the exact CourseLock address and hashes.
- Hosted GenLayer web/model providers: are a runtime trust boundary for retrieval and model availability, not a source of legal truth.

## Attack classes and mitigations

| Attack | Mitigation / residual risk |
|---|---|
| Forged promisor representation or position | `publish_representation` and `open_position` require the recorded promisor sender. Hashes bind course, author, representation, reliance, evidence, and position. |
| Counterparty impersonation | Acceptance, reliance, and evidence submission require the designated counterparty sender. Live unauthorized acceptance and representation attempts finalized with contract errors. |
| Course owner bypass after reliance | Course scope and participant identity are frozen. Withdrawal and closure stop future operations but do not erase prior commitments or records. |
| Reliance committed after withdrawal | `commit_reliance` requires an active course and active representation. The live withdrawal case rejected a new reliance while preserving the old record. |
| Stale representation or evidence substitution | Expected representation, commitment, and evidence hashes are required at each later boundary. Live stale calls finalized with contract errors. |
| Fabricated quote | Each leader and validator independently fetches the selected URL and checks exact quote occurrence before semantic classification. Quote presence is necessary, not sufficient. |
| Misleading surrounding context | Prompts require full-page/context review; validator independently classifies action support. A public page can still lie or omit facts; this remains a provenance risk. |
| Prompt injection in page, quote, or caller text | Delimited values are treated as untrusted data; instructions inside them are not followed. Validators independently re-run the material check. |
| Namespace confusion / SSRF-style URL | URL normalization requires HTTPS, ASCII, no controls/backslash/query/fragment/percent encoding, no userinfo/ports, valid DNS labels, no IP-like numeric/hex/wrapper names, no known local/private suffixes, and no path traversal. This is not authenticated source ownership, and hosted redirect/DNS policy remains outside the contract. |
| Leader fabricates contradiction | Validator independently classifies relation, same action, and reversal, then runs a bounded compatible-reading audit for exceptions, changed actors/actions/dates, qualifications, and scope. |
| False clearance | `can_enforce` is deterministic and requires `CLEARED`, `CONFIRMED`, and exact hashes. Unresolved, ambiguous, unrelated, pending, rejected, or malformed cases do not clear. |
| Malicious or unavailable validator | Disagreement, malformed output, unavailable web, or unavailable model cannot become affirmative proof or clearance. A transaction may finalize as disagreement/undetermined with no state transition. |
| Consumer replay | `CourseConsumer` requires a 64-character lowercase-hex action ID and records it once. Live replay finalized with `ACTION_ALREADY_EXECUTED`; count remained `1`. |
| Consumer unauthorized use | Consumer constructor records its executor; every write requires that sender. Live counterparty use finalized with `ONLY_EXECUTOR`. |
| Consumer stale/unrelated receipt | Consumer calls the typed CourseLock `can_enforce` view with the exact attempt and three hashes. A blocked live attempt finalized with `NO_COURSELOCK_CLEARANCE`. |
| State/storage spam | Text, page, and URL lengths are bounded; per-course, per-representation, per-reliance, and per-reliance-attempt counts are capped. Global transaction spam remains a chain-level concern. |
| Reentrancy / fund theft | No funds, token transfers, callbacks, administrator override, upgrade path, or external writes exist in the primary. The consumer performs only a typed view before its own local write. |

## Assumptions

1. StudioNet validators execute the pinned contract source under the declared GenVM runtime and the consensus mechanism supplies independent validator paths.
2. `gl.nondet.web.render` can independently retrieve the same public source often enough for an affirmative decision; source mutation can instead produce disagreement or inconclusive proof.
3. Participants control their signing keys. CourseLock authenticates wallet addresses, not names, organizations, or legal identity.
4. Consumer integrators verify the deployed primary address and pass the exact binding tuple; a consumer that ignores `can_enforce` is outside this protocol’s guarantees.
5. Public evidence namespaces are mutually accepted scopes, not cryptographic publisher identity proofs.

## Residual risks

- A public source may be self-authored or misleading. The live README demonstration explicitly makes this limitation visible.
- Redirect behavior, DNS resolution, content freshness, and provider egress controls are hosted-runtime policies; the contract can reject unsafe URL spellings but cannot authenticate DNS ownership.
- Natural-language classifications can be wrong even when validators agree. The adversarial audit reduces, but does not eliminate, semantic error.
- A promisor can refuse to open a position or act off-chain. CourseLock is a participating enforcement gate, not a coercive mechanism.
- The npm dependency tree reported advisories during installation. These are development-tooling supply-chain warnings; the deployed Python source has no runtime dependency on npm packages. The CLI pin was not changed with an automatic audit fix because that could violate the mandated `0.39.1` environment.
