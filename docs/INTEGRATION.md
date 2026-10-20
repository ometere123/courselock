# CourseConsumer integration

`contracts/course_consumer.py` is a minimal Intelligent Contract proof that another contract can consume CourseLock’s final predicate. It is not an application backend, wallet integration, escrow, token transfer or generic permission system.

## Required bindings

A consumer must pin:

1. the verified CourseLock address on stable StudioNet `61999`;
2. the exact attempt ID;
3. the representation hash from `get_representation`;
4. the commitment hash from `get_reliance`;
5. the position hash from `get_attempt`;
6. the exact downstream action payload;
7. the one-time 64-character lowercase-hex action ID.

The consumer must never interpret `is_protected == false` as clearance. Unknown, open, retryable, unresolved, blocked, stale, unrelated or mismatched records are not positive authorization. Only `can_enforce(attempt_id, representation_hash, commitment_hash, position_hash) == true` authorizes the consumer’s own action.

## Contract behavior

The constructor accepts a typed CourseLock `Address` and records the deploying sender as `executor`.

`commit_action(attempt_id, representation_hash, commitment_hash, position_hash, payload)` then:

- requires the executor;
- validates all three 64-character lowercase-hex hashes and the bounded non-empty payload;
- calls the typed CourseLock `can_enforce` view with the exact tuple;
- computes the domain-separated `COURSELOCK_CONSUMER_ACTION` payload hash over the attempt ID, three hashes and payload;
- stores one immutable `ActionIntent` for that attempt with the committing executor.

`execute(attempt_id, representation_hash, commitment_hash, position_hash, payload, payload_hash, action_id)` then:

- requires the same executor;
- validates the exact intent and payload hash;
- rejects action-ID replay and reuse of an already executed intent;
- calls the typed CourseLock view again, so a stale or substituted receipt cannot pass;
- records its own `Execution`, marks the intent executed, and increments the counter only after every check succeeds.

It never trusts caller-supplied status text and never assumes a failed asynchronous transaction finalized successfully. A finalized receipt and a counter/intent readback are required.

## Hardened live proof

- CourseLock: `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E`
- CourseConsumer: `0x6381F1703BFBc80ff151EB2EC3Be585aB5e3aE5C`
- Executor: `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7`
- Blocked commit: `0xe699f9e80d4f183deedbc92686919ba8970db48bd0124d80097ad151ba06b574` → finalized `NO_COURSELOCK_CLEARANCE`; count `0`.
- Cleared intent commit: `0xea68c70bba8cf42659195fb289adc3ea0b76d0441f0d4ac9bf019180ee45e0af` → finalized; exact payload hash `192e7eeae9bb8a0db5df80d3f34ddc7536fa24d24660364c37d781be132923e0`.
- Exact execution: `0xfc5519ff9187094e285ac0d081f388efe958b27f00ab6bc42a3a1ca060476cf3` → finalized success; count `1`, intent `executed=true`.
- Replay: `0xaf9b5984bfd58f8fbbe5248955fc47dfd38031c00d2df5fa86e600b2d7ccbeea` → finalized `ACTION_ALREADY_EXECUTED`; count stayed `1`.
- Payload substitution: `0x49b41b76f71d8b638a32ee4e42709fbc98f43ef2d5781408bdef8346c736ad4f` → finalized `PAYLOAD_BINDING_MISMATCH`.
- Unauthorized executor: `0x17510b96f9bc1e90b1c6cd5556acc1b985fd6addacfa38e65e6e1a086b8f0764` → finalized `ONLY_EXECUTOR`.

This is a real typed cross-contract view call on StudioNet. It proves the consumer gate and bindings were executed on-chain; it still does not prove that a real-world action occurred. The primary contract’s public-evidence limitation applies to the consumer’s input.
