# CourseConsumer integration

`contracts/course_consumer.py` is a minimal optional proof that another Intelligent Contract can consume CourseLock’s final predicate. It is not an application backend, wallet integration, escrow, or generic permission system.

## Required bindings

A consumer must pin:

1. the verified CourseLock address on stable StudioNet `61999`;
2. the exact attempt ID;
3. the representation hash from `get_representation`;
4. the commitment hash from `get_reliance`;
5. the position hash from `get_attempt`;
6. a unique 64-character lowercase-hex application action ID.

The consumer must never interpret `is_protected == false` as clearance. Unknown, open, unresolved, blocked, stale, unrelated, or mismatched records are not positive authorization. Only `can_enforce(attempt_id, representation_hash, commitment_hash, position_hash) == true` authorizes the consumer’s own action.

## Contract behavior

The constructor accepts a typed CourseLock `Address` and records the deploying sender as `executor`. `execute(...)` then:

- rejects non-executor senders;
- validates the three 64-character lowercase-hex binding hashes and action ID;
- rejects action-ID replay;
- calls the typed `ICourseLock(...).view().can_enforce(...)` cross-contract view;
- writes its own `Execution` record and increments its counter only after the view returns true.

It never trusts caller-supplied status text and never assumes a failed asynchronous transaction finalized successfully. A transaction receipt and a counter readback are required.

## Final live proof

- CourseLock: `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167`
- CourseConsumer: `0xaa8a5Cd74f6A0f82A4413AF0a8ce71Bb09DcbF90`
- Executor: `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7`
- Blocked attempt transaction: `0x266798a07a37c4c49e5dcdfeea65437ce532a1aa24f88f651441192f325026a8` → finalized rollback `NO_COURSELOCK_CLEARANCE`; count stayed `0`.
- Unauthorized wallet transaction: `0x1d1201a1e559dfab46dc636c702d2b8bcd3b2efea84925ac0691ec0348285cc8` → finalized rollback `ONLY_EXECUTOR`.
- Cleared attempt transaction: `0x92fd3e68174d02d83e5878fc4e2b466af0cb3df9c1520f808a3d41625ff606c9` → finalized `SUCCESS`; count became `1`.
- Replay transaction: `0x711d901477fdebc417ccebf82b08f869341a7f7f11917aac433d4650b2099d41` → finalized rollback `ACTION_ALREADY_EXECUTED`; count remained `1`, `was_executed(...) == true`.

This demonstrates a real typed cross-contract call on-chain. It still does not prove that a real-world action occurred; the primary contract’s public-evidence limitation applies to the consumer’s input.
