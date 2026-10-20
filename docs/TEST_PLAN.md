# CourseLock test plan and results

The repository distinguishes deterministic offline tests, GenVM Direct Mode, and live StudioNet. A green fake-runtime or Direct Mode test is never presented as live consensus proof.

## Final local commands and results

| Check | Exact command/result |
|---|---|
| Offline tests | `python -m pytest tests -q` → **48 passed** |
| Structural checks | `python scripts/preflight.py` → **22 checks passed** |
| Source consistency | `python scripts/source_consistency.py` → passed |
| Python syntax | `python -m py_compile contracts/courselock.py contracts/course_consumer.py` → passed |
| JavaScript syntax | `node --check scripts/deploy_studionet.mjs` and `node --check scripts/assert_studionet.mjs` → passed |
| Direct Mode dependencies | `genlayer-test==0.29.0`, `genlayer-py==0.11.0`, `pytest==8.4.2` |
| Direct Mode | `& '...\\gltest.exe' direct_tests -v -s` → **34 passed** |
| Native validator API | `VMContext.run_validator()` supported and exercised in Direct Mode; callback agreement is not a substitute for live rollback |
| GenVM linter | `genvm-linter==0.11.0`, `GENVM_VERSION=v0.3.0-rc7`, both contracts validated; only informational `I200` |
| Stable network guard | `node scripts/assert_studionet.mjs` → `eth_chainId=0xf22f`, decimal `61999` |
| Local CLI | repository-local `genlayer --version` → `0.39.1` |
| Dependency audit | `npm audit --omit=dev --audit-level=high` → zero findings; full tree has two moderate nested development-tool advisories |
| Mutation checks | Two executable invariant mutants: terminal proof guard and party-only assessment; both alter a relevant regression outcome when mutated |

The Direct Mode suite covers typed/nonzero address conversion, course ownership/acceptance, duplicate and unauthorized calls, stale hashes, withdrawal/closure history, URL namespace hardening, evidence shape/quote failures, retry/recovery and exhausted limits, independent native validator callbacks, malicious leader classifications, positive clearance audits, third-party assessment griefing, consumer payload binding, executor authentication and replay. It contains 34 meaningful tests rather than duplicated scenario labels.

## Live StudioNet coverage

The hardened deployment used stable `studionet` chain `61999` at `https://studio.genlayer.com/api`, with CourseLock `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E` and CourseConsumer `0x6381F1703BFBc80ff151EB2EC3Be585aB5e3aE5C`.

Course 3 is the fully captured final lifecycle, using promisor `party_a` (`0xac3ac69dc0bde389256dd6748c75817ead9286d9`) and counterparty `party_b` (`0xa7eeae0e93793e3146cb14b0700251b8b0ebadfb`):

| Step | Finalized transaction/readback |
|---|---|
| Course creation | `0x27bb1ecf0f6c8337ef7abd00bc7e5629b746fd58eccf51c54dc6125d1ae98fe4`; course `3`, status `ACTIVE` after acceptance |
| Counterparty acceptance | `0x042081bb3e0c1ab43065ec3fb989c0da8563696c0918c7c807ecce3b0f56194b`; `MAJORITY_AGREE` |
| Representation | `0xdcf988206516dfaf27b438923aed6209c3c237a673412ddeeb21444d248f6fe0`; representation `2`, hash `2e83bcb17cd46d97eb86877eaf51e2c6602a2028b9ab7862b8d9424878755a6a` |
| Reliance commitment | `0xd1780cc24aa5fe969d5b883cd76176d896f16df5e80dc56d50c7c6e6f093233d`; reliance `2`, commitment `4d9803420cd72616e4af968b3e533fe174f3a4d72e442be9406b48edb6dc73b4` |
| Evidence consensus | `0x8b54f31eaa0856e04074174faf37576c6c3aa4f72b1518edc3c1a236e2b65737`; `CONFIRMED`, evidence hash `7462d8f39d3af499b20f6d8aa71a8aa8657a70049d26cceb269c0147dc41d2fe`, one proof attempt |
| Contradiction position | `0x09c45b894b7014336ab802360a34d4ab31428f0f24a75432a46ff7d9149c6911`; position `5`, hash `aaf2f9421bd2feae5f8d2bc69470b5807072e83e6e74652f81f0dbb252a720fc` |
| Contradiction assessment | `0xbe5caca2b5ac329f06c9b5fefe6d4d195d2483fa5874276a2edf6c76d91d3bc0`; readback `BLOCKED`, `CONTRADICTORY`, `same_action=true`, `reverses_treatment=true` |
| Consistent position | `0xc11bacffbc8113a42b3cfe6943a98c8a8b2431bad7ec15995c5d15c17936ef6b`; position `6`, hash `fa6addfd498381ee30cee1d35ef50bf6d917443800ee85f1543cf0f269d93fd1` |
| Consistent assessment | `0xd574f5d08a8f256e2b5fd6a12dd8a5bef5c009b7942eed75ac5d6425d8510bfa`; readback `CLEARED`, `CONSISTENT`, `same_action=true`, `reverses_treatment=false` |
| Exact consumer predicate | `can_enforce(6, 2e83…5a6a, 4d98…73b4, fa6a…3fd1) == true` |
| Stale binding | `0xba8229f12752cd38b40da1df4b092c92683565a41d4c21d466e936a76588675d`; finalized contract error `STALE_BINDING` |

Course 1 supplied the historical/recovery and consumer evidence. Its confirmed reliance remained readable after withdrawal and closure; its contradiction attempt was `BLOCKED`, its compatible attempt was `CLEARED`, and its non-decisive attempt finalized `UNDETERMINED / MAJORITY_DISAGREE` with the attempt still `OPEN` and `can_enforce=false`.

## Consumer live proofs

The deployed consumer executor is `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7`.

- Blocked CourseLock intent: `0xe699f9e80d4f183deedbc92686919ba8970db48bd0124d80097ad151ba06b574` → finalized `NO_COURSELOCK_CLEARANCE`; count stayed `0`.
- Exact intent commit for cleared attempt `2`: `0xea68c70bba8cf42659195fb289adc3ea0b76d0441f0d4ac9bf019180ee45e0af`; readback payload hash `192e7eeae9bb8a0db5df80d3f34ddc7536fa24d24660364c37d781be132923e0`.
- Exact execution: `0xfc5519ff9187094e285ac0d081f388efe958b27f00ab6bc42a3a1ca060476cf3` → finalized success; count became `1`; intent `executed=true`.
- Exact replay: `0xaf9b5984bfd58f8fbbe5248955fc47dfd38031c00d2df5fa86e600b2d7ccbeea` → finalized `ACTION_ALREADY_EXECUTED`; count remained `1`.
- Payload substitution: `0x49b41b76f71d8b638a32ee4e42709fbc98f43ef2d5781408bdef8346c736ad4f` → finalized `PAYLOAD_BINDING_MISMATCH`.
- Unauthorized wallet: `0x17510b96f9bc1e90b1c6cd5556acc1b985fd6addacfa38e65e6e1a086b8f0764` → finalized `ONLY_EXECUTOR`.

## Adversarial cases and limits

The deterministic and Direct Mode tests inject malformed JSON, truncated results, prompt-injection strings, missing/fabricated quotes, changed or misleading context, namespace confusion, wrong hashes, malicious leader classifications, validator disagreement, provider failures, recovery substitution and retry exhaustion. Both leader and validator callbacks are exercised where the native Direct Mode API supports them.

StudioNet is not used as a deterministic hostile-web fixture. The live run validates the real public evidence, final consensus statuses and exact cross-contract state readbacks; the broader hostile-web and provider-failure matrix remains reproducible Direct Mode coverage. No test asserts subjective reliance, wallet-to-website identity, website ownership, physical action completion, or legal liability.
