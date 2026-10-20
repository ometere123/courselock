# Consensus/equivalence contract

## Frozen input boundary

The source-assessment boundary captures: course.scope, authenticated representation.text, precommitted reliance.action, chosen `evidence_url` and `evidence_quote`. The URL must fall within the prefix previously authenticated by both party accounts. No storage reads/writes inside nondeterministic blocks. The URL and quote become immutable record fields after a consensus outcome; no edits.

For proof, leader/validators each call `gl.nondet.web.render(url, mode="text")` on the same URL; an absent exact quote is a deterministic negative proof outcome. Presence is necessary, not sufficient: each independently asks if the whole page supports **completed action** by the relevant counterparty under the original scope. A statement of intent is not enough. Conclusive proof requires both source availability and semantic corroboration.

The position boundary freezes scope, original representation, precommitted action, previously confirmed verbatim evidence quote and promisor's authenticated later position. Leader/validators independently derive three material fields: relation (1 CONSISTENT; 2 CONTRADICTORY; 3 UNRELATED; 4 AMBIGUOUS), `same_action` and `reverses_treatment`. A claimed contradiction must have a witness and withstand a separate adversarial search for a reasonable compatible interpretation, exception or distinct actor/action. A merely cosmetic wording change is never material contradiction.

## What consensus actually agrees on

- Proof: status only; reason code is explanatory leader text.
- Position: relation, same_action, reverses_treatment. Witness/reason may differ; no claim they were independently accepted word-for-word.
- Disagreement causes validator rejection; an unavailable/malformed model yields inconclusive/ambiguous, never a grant.
- The deterministic state machine alone sets final status and exposes public consumer gates.

## Why two boundaries

The proof and the later position are at **different moments** and may require different validators/evidence. Collapsing them into one LLM call would let the promisor choose a story about an act without first establishing that the counterparty's precommitted action has credible public corroboration.

## Known epistemic limits

Consensus cannot establish subjective reliance motives, website ownership, actual chronology of physical acts or legal estoppel. A party can still lie on an approved public site; evidence cannot exceed the trustworthiness of that site's provenance. Two agents may interpret ambiguous prose alike and still be wrong. Consumer enforcement applies **only** when downstream contracts opt in to the exact pinned tuple; no external contract is forcibly constrained.
