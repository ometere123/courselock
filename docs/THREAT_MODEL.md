# Threat model

| Attack | Defence / limitation |
|---|---|
| Forged promisor promise | `publish_representation` and `open_position` require recorded promisor wallet sender. |
| Counterparty invents a course alone | `accept_course` is required before representation/reliance. |
| Reliance invented after promise withdrawn | `commit_reliance` only while course+representation active. Withdrawal never retroactively destroys prior. |
| Repromise substitution | immutable representation hash bound at reliance commitment. |
| False action proof via fabricated quote | quote must be verbatim in independently fetched agreed-namespace page; validator judges full surrounding context and completed act. Does not prevent false statements by an accepted publisher. |
| Source injection telling model to approve | page/quote/promise/position explicitly untrusted in prompts; validators independently re-run and compare material statuses. |
| External/private URL | HTTPS prefix vetted at course acceptance, no input fetch outside frozen namespace. GenVM must enforce actual DNS/redirect/network restrictions. Full IP/redirect/SSRF hardening remains a final audit task. |
| Changed webpage between leader/validator | independent re-fetch/disagreement prevents consensus. Dynamic page stability must be verified live. |
| Evidence URL switched after receipt | evidence hash freezes URL, quote, proof status, and reliance commitment. No second proof attempt. |
| Leader invents a contradiction | validator independently compares the material relationship and adversarially searches for compatible reading. |
| Ambiguous contradiction incorrectly blocked | ambiguous outcome is unresolved, not legally certified blocked; consumer never obtains clearance. |
| Leader invents a clearance | validator independently rechecks relation, applicability, and non-reversal. Consumer requires exact pinned hashes. |
| Replay in downstream consumer | `CourseConsumer` stores one-time `action_id` with `position_hash`. |
| Malicious promisor refuses to open a position | CourseLock only gates participating enforcement paths; it cannot compel a promisor to call it or stop unrelated off-chain behaviour. |
| Unbounded state/spam | per-course representations, per-representation reliances, per-reliance attempts, and text lengths bounded. Global openings still subject to chain fees. |
| Reentrancy / funds safety | no funds, no callbacks or external writes in primary. Consumer does only a typed view. |
| Race with withdrawal | on-chain ordering determines whether reliance was committed before withdrawal; no external-time assumption. |
| Semantic collisions | the source prefix is fixed per course and role/status hashes pin individual commitment instances. |

**Remaining final review**: verify actual chain input types, test on-chain `Address` semantics and `gl.nondet.web.render` responses, inspect redirects/IPv4 private URL bypasses and hosted namespace behavior. Do not claim these verified merely because mocked Python passed.
