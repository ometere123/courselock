# Evidence ladder and completion criteria

## Verified in this generation environment

- `python -m pytest tests -q`: 32 passed offline mock-runtime tests.
- `python scripts/preflight.py`: 16 structural checks passed.
- `python -m py_compile contracts/*.py` and `node --check`: syntax passed.

**What this is NOT**: GenVM Direct Mode, live web consensus, a production build, a source-matched chain deployment, or proof the optional consumer is deployed.

## Mandatory Codex Direct Mode work before submission

1. Install `genlayer-test==0.29.0` and correct stable GenVM test SDK; run and expand `direct_tests/test_courselock_direct.py` to **full dual-account coverage**.
2. Test actual sender switching with an A promisor, B counterparty, and C unauthorised outsider; confirm representation can't be spoofed and B must explicitly accept.
3. Independently mock source fetch in leader/validator; verify exact-quote absence, misleading context, instruction injection, page unavailability, changed source content, HTTP failure, source namespace escape, oversized page, invalid JSON and truncated output.
4. Independently mock contradictory/consistent/unrelated/ambiguous conclusions; validator must substantively disagree with malicious leader when warranted; positive contradiction must survive adversarial compatible-reading check.
5. Verify withdrawal/closure affects only *future* reliance; frozen existing reliance/attempts remain readable and settleable.
6. Verify stale representation/commitment/evidence/position hashes cannot provide clearance, consumer read binds all exact values, and replayed consumer action ID is refused.
7. Validate both primary/consumer contracts' ABI and storage serialization on actual GenVM; fix `Address`, TreeMap, typed interface or event inconsistencies if any.
8. Run `gltest direct_tests -v -s` until entirely passing with screenshots/logs, and update this document with a source-matched test report. Do not mark unrun tests passing.

## Mandatory StudioNet 61999 finalization

1. `npm install`, verify repo-local CLI `0.39.1`, verify RPC `eth_chainId=0xf22f` (61999 decimal), select `studionet` exactly.
2. Deploy the exact primary source, record tx/hash/address, await **finalization**, verify explorer source parity and contract schema.
3. Deploy optional consumer with the finalized CourseLock address and verify typed read.
4. Run source-matched lifecycle with two distinct wallets/identities: consent, publish, reliance, valid proof and three new positions (contradictory, consistent, ambiguous). Record both positive and negative case receipts.
5. Verify `CourseConsumer` refuses BLOCKED/UNRESOLVED and accepts CLEARED once. Read back `get_count()==1` and reject duplicate action.
6. Include raw command outputs, transaction hashes, finality, code hash and source hashes in `DEPLOYMENT.md`; verify **61999** in every run.
7. Run repository tests/CI successfully after any changes; no unresolved TODOs/failed tests at submission.
