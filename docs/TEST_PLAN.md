# CourseLock test plan and results

The repository distinguishes the deterministic offline fake runtime, GenVM Direct Mode, and live StudioNet. A green local mock test is never presented as a live consensus result.

## Final local commands and results

| Check | Exact command/result |
|---|---|
| Offline tests | `python -m pytest tests -q` → **32 passed** |
| Structural checks | `python scripts/preflight.py` → **16 checks passed** |
| Python syntax | `python -m py_compile contracts/courselock.py contracts/course_consumer.py` → pass |
| JavaScript syntax | `node --check scripts/deploy_studionet.mjs` and `node --check scripts/assert_studionet.mjs` → pass |
| Direct Mode dependencies | `genlayer-test==0.29.0`, `genlayer-py==0.11.0`, `pytest==8.4.2` |
| Direct Mode | Windows equivalent full-path command `& '...\\gltest.exe' direct_tests -q -s --tb=short` → **26 passed** |
| GenVM linter | `genvm-linter==0.11.0`, `GENVM_VERSION=v0.3.0-rc7 genvm-lint check ... --json` → primary and consumer validation pass; only informational `I200` |
| Stable network guard | `node scripts/assert_studionet.mjs` → `eth_chainId=0xf22f`, decimal `61999` |
| Local CLI | repository-local `genlayer --version` → `0.39.1` |
| Dependency audit | `npm audit --omit=dev` → zero findings; full tree → two moderate nested `dockerode`/`uuid` development-tool findings, zero high/critical |

The Direct Mode suite contains 26 meaningful tests rather than 60 duplicated functions. It covers typed/nonzero address conversion, course ownership/acceptance, duplicate and unauthorized calls, stale hashes, withdrawal/closure history, URL namespace hardening, evidence shape/quote failures, proof and position fail-closed behavior, malicious-result cases, consumer hash/executor/replay checks, and the status dictionary. Direct Mode uses the local test harness; it is not a StudioNet transaction.

## Live StudioNet coverage

The finalized run used distinct wallet identities:

- Promisor: `praest-deployer`, `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`
- Counterparty: `party_b`, `0xA7EeAE0E93793e3146Cb14b0700251B8b0EBADFB`

The live run covered:

- course creation, explicit acceptance, duplicate acceptance, and unauthorized acceptance;
- promisor-only representation publication and unauthorized representation attempt;
- correct and stale reliance commitments;
- confirmed public quote fetched from an immutable GitHub raw URL;
- stale position binding;
- genuine contradiction → `BLOCKED`, `is_protected=true`, `can_enforce=false`;
- genuine compatibility → `CLEARED`, exact `can_enforce=true`;
- ambiguous assessment finalized as `UNDETERMINED/MAJORITY_DISAGREE`, leaving the attempt `OPEN` and `can_enforce=false`;
- representation withdrawal rejecting new reliance while preserving earlier history;
- invalid quote → `REJECTED/QUOTE_ABSENT` and course closure rejecting new representation;
- typed CourseConsumer cross-contract block, executor rejection, successful clear, and replay rejection.

The live evidence table and every critical receipt hash are in [DEPLOYMENT.md](../DEPLOYMENT.md).

## Adversarial cases and limits

The deterministic and Direct Mode tests inject malformed JSON, truncated results, prompt-injection strings, missing quotes, changed/misleading context, namespace confusion, wrong hashes, and malicious leader classifications. The leader and validator callbacks are both exercised by the test fixtures, including disagreement rejection and compatible-reading rejection.

StudioNet cannot safely be used as a deterministic unit-test fixture for arbitrary hostile web pages or validator scheduling. The live run therefore validates the real public evidence, two independent consensus boundaries, and final state readbacks; the broader hostile web matrix remains a reproducible Direct Mode regression suite.

No test asserts subjective reliance, wallet-to-website identity, website ownership, or legal liability. Those are documented trust limits, not hidden protocol guarantees.
