# CourseLock deployment evidence

This file records the completed stable-network run. Values below are from StudioNet RPC receipts and readbacks, not placeholders.

## Locked environment

- Network: `studionet`
- Chain ID: `61999` (`0xf22f`)
- RPC: `https://studio.genlayer.com/api`
- Repository-local CLI: `genlayer@0.39.1`
- Global CLI used: **NO**
- GenVM linter: `genvm-linter==0.11.0`, primary and consumer validation passed
- Pinned contract runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- RPC guard: `node scripts/assert_studionet.mjs` confirmed `eth_chainId = 0xf22f`

The repository-local deployment guard checked the package pin, ran the RPC guard, selected `studionet`, displayed the CLI network readback, and required the literal confirmation `DEPLOY-61999`. Deployment was not performed with a CLI `--rpc` override; the local CLI’s built-in `studionet` configuration was used after the RPC assertion.

## Primary deployment

- Source: `contracts/courselock.py`
- Signer: `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`
- Address: `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167`
- Deployment transaction: `0x3654a638f09b9b1909c7e6b75f40cd9af8c88b7c2ffb30a0760a541938c5cfd3`
- Final chain status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- Explorer base: [GenLayer Explorer](https://genlayer-explorer.vercel.app)

The final receipt was read back after submission with the local GenLayer client and returned status code `7` / `FINALIZED`, result code `6` / `MAJORITY_AGREE`. The chain-exposed source was retrieved through `gen_getContractCode` and compared byte-for-byte.

## Consumer deployment

The consumer was deployed through the repository-local `.\node_modules\.bin\genlayer.cmd` using a typed `addr#...` constructor argument for the finalized primary address.

- Source: `contracts/course_consumer.py`
- Constructor CourseLock address: `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167`
- Signer/executor: `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`
- Address: `0xaa8a5Cd74f6A0f82A4413AF0a8ce71Bb09DcbF90`
- Deployment transaction: `0xbd2d2472b8238ee7d7aee0b6e2326790a684db1aae9afe65c95d1366af97ede6`
- Final chain status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- Explorer base: [GenLayer Explorer](https://genlayer-explorer.vercel.app)

The deployed consumer’s `get_executor()` readback was `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7` (case-normalized by the view client).

## Source integrity

| Source | Local SHA-256 | Deployed SHA-256 | Exact bytes |
|---|---|---|---|
| `contracts/courselock.py` | `c5d06e1de41d0fc7a0982575f66fe293151b8afd90078550e2da9cfe0b1b537a` | `c5d06e1de41d0fc7a0982575f66fe293151b8afd90078550e2da9cfe0b1b537a` | yes |
| `contracts/course_consumer.py` | `62ffdf651e1e5bd6b0808776e6c0afab3cc4c23424877e56a646988d5e428257` | `62ffdf651e1e5bd6b0808776e6c0afab3cc4c23424877e56a646988d5e428257` | yes |

Method: read each deployed source with the StudioNet `gen_getContractCode` RPC through the repository-local GenLayer JS dependency, hash the UTF-8 response with SHA-256, and compare against the working-tree files. The final Git commit must be checked against these same files before release; later documentation-only commits do not change the deployed contract bytes.

## Live evidence namespace

The demonstration froze this immutable public namespace:

`https://raw.githubusercontent.com/ometere123/courselock/198b6089f1a10db196d76289aea58e12824ab74a/`

Evidence URL:

`https://raw.githubusercontent.com/ometere123/courselock/198b6089f1a10db196d76289aea58e12824ab74a/README.md`

Exact quote independently retrieved and consensus-accepted:

> CourseLock makes a previously authenticated representation and a counterparty's *pre-action* commitment part of the required enforcement history.

This is a bounded public-content demonstration. The page proves that the quoted content was retrievable at an immutable GitHub commit; it does not prove website ownership, wallet-to-GitHub identity, subjective reliance, or a real-world physical action.

## Finalized CourseLock lifecycle receipts

All critical receipts below were later read back as `FINALIZED`. Transaction status `FINALIZED` means the chain reached its decided terminal state; contract-level negative cases can still have a finalized transaction whose execution result is an error/rollback.

### Course 1 — contradictory position blocked

| Step | Result |
|---|---|
| `open_course` | tx `0x45cb90957e1c874346fc45a9b04d579789095f1a4937f1543ddb710c5fbf9b79`; readback course `1`, status `OFFERED`, frozen course hash `1ed2d500b3ce8a65398b6e88909b60d778830bca2257acceba58a04825291d7f` |
| Unauthorized promisor acceptance | tx `0x786cb3919a021e59046e8d2334cf5879697296d32a46500bf0080a47a38ad85d`; finalized contract error |
| Counterparty acceptance | tx `0xd697291c4ec328945cfe7f85e660daa8f442d788297fb7276217772acfe1ad00`; readback status `ACTIVE` |
| Duplicate acceptance | tx `0x137d08d38ca8521a96e1f89b02b4ead2bb3e816e8eed6d5ec64c1d8533fc78fd`; finalized contract error |
| Unauthorized representation | tx `0x55ff4dc0cd929744ecace0a73ab5cb5eb07ac8258ba4c3b372b7485cad7d2dfa`; finalized contract error |
| Representation | tx `0x438bf716ee565a95adb151a0390853393b0f43ca6b5a2945fa28fdaa21cc5328`; representation hash `7dd5283a628783d692f5f5b3503120574cac5df76cbc314a1c43ea0710e6c154` |
| Stale reliance hash | tx `0x43e1fb100f6dcc69b3a6583e113d62a9b5791373358af9c5c4bc5868e7e188b6`; finalized contract error |
| Reliance commitment | tx `0x87a7d339aaab1c75fe4ba5340533a9d5e0f9eaecd79e2e2ec31e9e6bf4ec89d7`; commitment hash `04c46a1354ebb48049f4733b5029205609aad41abc843338295af4fc0d7a0896` |
| Stale position binding | tx `0x78ae4f2dcd9625e9bea0ae6d962ad39488ee6dedbaade7cc7d33e9b23e4b56d3`; finalized contract error |
| Evidence consensus | tx `0x721316dd63f5fe9ef070a666965cebca5a24ed0aca1580620189a9693348be8e`; readback `CONFIRMED`, reason `VERBATIM_MATCH_CONFIRMED`, evidence hash `9d1df2f4e0224eb589aed56caefc2936e9ee4054750f27ea5e6e3b7736592e43` |
| Contradictory position | tx `0x4f24fec5c34f99fb7dd63e272e3e654659dd7481f2649ad30ebc339f2355228b`; position hash `eb8978b070b534abc7c2d646f530d592a7fe9d1d3e814524c9902cc29c84ca7b` |
| Assessment | tx `0xb46e488e425a0934059f9585b2987828fc114eb95a9a14a6dc0feb19cefecd74`; readback `BLOCKED`, relation `CONTRADICTORY`, `same_action=true`, `reverses_treatment=true`, witness `DIRECT_NEGATION_SAME_ACTION` |
| Consumer gate | `is_protected(1) == true`; `can_enforce(1, ...) == false` |

### Course 2 — consistent position cleared and ambiguity denied

| Step | Result |
|---|---|
| Course/acceptance | open tx `0xac980e593aa9928705ed64cf1353b8ba5e1b71f8f6f2a0ae8f94c323a990fd43`; accept tx `0xe1b5be809b8c8e4f3ce6a0c1f95f29325f0ea34cf420071a96cd4f20a37e7924` |
| Representation | tx `0xfcc417e238737fc9c9c029cc87bee16e7128f7667d66585de1220ad7319db49b`; hash `23fdb6efd347f14794cf617b2e0c411b1d708d885e367fb6db5925d5229bab7c` |
| Reliance | tx `0x473061deba3bf3e940abddd7e275063f9ca1f555a9799c7ee77844521b3c1de2`; commitment hash `8e01875fe5f6c4061e6119518ec890188e023382133cfc72f44e39c66e31de87` |
| Evidence | tx `0x96d783e6e56a1545c54cf68f7d3ab4d6301c557b5b901330f3f5f0cdbd765529`; readback `CONFIRMED`, evidence hash `2f79b95a2d421842615a578eba47d9ffe8daa429c487bdd1942396dbd264eda7` |
| Consistent position/assessment | open tx `0x2fc361fdab3c5b1ab4ece6a2b64122baabe9b7b27329eb8366b1231744e16a99`; assess tx `0xd43e07d834d323360c38fa2e6764a9f18c02f5f2169ff3d4d75e343e2142c4bc` |
| Cleared readback | attempt `2`, status `CLEARED`, relation `CONSISTENT`, `same_action=true`, `reverses_treatment=false`, position hash `c075ef4bdc0fc083b98c1ba75d73ec960595eeb55879f19cdde3dfdaec25528d`; `can_enforce(...) == true` |
| Ambiguous position | open tx `0x9bb263389b622a437563f248b6b2f96beac046188992a601a067af153a0a8343`; assess tx `0x9686d5e63444b49d640ac45b12c6463057f1c503571d2607f30589f6bc653c64` finalized `UNDETERMINED` / `MAJORITY_DISAGREE`; attempt remains `OPEN`, and `can_enforce(...) == false` |

### Course 3 — withdrawal and closure preserve history

- Reliance was committed in tx `0x65923ee1fb7aff17f89a73e308cc4462b1fb9fc6928a2f00f899e442027cd4c2` with commitment hash `e4ec8af0071fd79bab71ab1d1fab6ab53601dc5098a6f7fb030be5b402733088`.
- Withdrawal tx: `0xfbf06bb25815e56dd117edc397a2da9772164b87a8e8fb04d09f262d0f4e0945`.
- New reliance after withdrawal tx `0xcf0bea4b0d7547abbd4f0cbc3ed2193cb19222dba66a1d23656882d554e59ea6` finalized with a contract error.
- The previously recorded reliance remained readable. An invalid quote was stored as `proof_status=REJECTED`, `proof_reason=QUOTE_ABSENT`, tx `0x9bd6208366258237cc1e17397af3b43901f02d310824dc97d8cb6080d2c09b26`.
- Closure tx: `0x81435898bc14e7e2d0b22aa3a38b8fb82842d4137a5dc561a27e305823853eac`; readback course status `CLOSED`.
- New representation after closure tx `0x78acf89cea56a745d9d15d1f04104d00aa77c665503128208b285dc09c08459c` finalized with a contract error.

## Cross-contract consumer proofs

The consumer deployment and all four execution receipts below were later read back as `FINALIZED` / `MAJORITY_AGREE`.

- Blocked CourseLock attempt: tx `0x266798a07a37c4c49e5dcdfeea65437ce532a1aa24f88f651441192f325026a8`; rollback `NO_COURSELOCK_CLEARANCE`; count remained `0`.
- Unauthorized counterparty wallet: tx `0x1d1201a1e559dfab46dc636c702d2b8bcd3b2efea84925ac0691ec0348285cc8`; rollback `ONLY_EXECUTOR`.
- Cleared CourseLock attempt: tx `0x92fd3e68174d02d83e5878fc4e2b466af0cb3df9c1520f808a3d41625ff606c9`; execution `SUCCESS`; count became `1`.
- Exact replay: tx `0x711d901477fdebc417ccebf82b08f869341a7f7f11917aac433d4650b2099d41`; rollback `ACTION_ALREADY_EXECUTED`; count remained `1`, `was_executed(64-hex-action-id) == true`.

## Reproduction commands

```sh
npm ci
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/preflight.py
node scripts/assert_studionet.mjs
node scripts/deploy_studionet.mjs
```

The primary guard requires `DEPLOY-61999`. Do not print or commit wallet secrets. The live lifecycle was run with the local `genlayer-js` package bundled by the pinned CLI so that typed `Address` constructor and cross-contract arguments could be verified without exposing a private key.
