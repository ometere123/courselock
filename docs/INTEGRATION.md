# Integrating CourseLock

Consumers should pin all of:

1. verified CourseLock contract address on stable StudioNet `61999`,
2. attempt ID returned by an authenticated promisor,
3. representation hash from the relevant `get_representation`,
4. commitment hash from `get_reliance`,
5. position hash from `get_attempt`,
6. application-specific action ID (64 lowercase hex characters).

A consumer must NEVER interpret `is_protected=false` as clearance. An unknown attempt and an unassessed attempt both return false. **Only `can_enforce(...) == true` authorizes the conditional action.**

`contracts/course_consumer.py` is a minimal separate optional IC. It calls the typed CourseLock `.view().can_enforce(...)`, then atomically stores a once-only action identifier. It does not send GEN or make an external web request. This makes replay and stale-position swaps visible in tests. A production consumer must also authenticate its executor role and bind the actual target/method/amount arguments to the action ID: this demo intentionally does not grant real economic authority.

A successful `can_enforce` is scoped to the **exact reliance action**, not a blanket release from all other course obligations.

## Contract interaction restrictions

Typed calls occur only in deterministic code. Do not call another IC from an LLM/web nondeterministic block. The primary does not mint tokens, move funds, communicate with external services beyond read-only web retrieval, or enforce legal rights against unwilling off-chain parties.
