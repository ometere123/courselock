# CourseLock deployment evidence

This file records the hardened stable-network deployment and the finalized transaction/readback evidence captured from StudioNet RPC. A finalized negative transaction is still a valid finalized transaction: its contract execution result is an error/rollback and its state mutation is absent.

## Locked environment

- Network: `studionet`
- Chain ID: `61999` (`0xf22f`)
- RPC: `https://studio.genlayer.com/api`
- Repository-local CLI: `genlayer@0.39.1`
- Global CLI used: **NO**
- GenVM linter: `genvm-linter==0.11.0`
- Direct Mode: `genlayer-test==0.29.0`
- Pinned contract runner: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- RPC guard: `node scripts/assert_studionet.mjs` confirmed `eth_chainId = 0xf22f`

The guarded primary command was run only after the local CLI version and RPC chain ID checks passed. The typed deployment confirmation was `DEPLOY-61999`. No private key was printed, hardcoded or committed.

## Hardened contract deployment

### CourseLock

- Source: `contracts/courselock.py`
- Signer: `0xA7EeAE0E93793e3146Cb14b0700251B8b0EBADFB`
- Address: `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E`
- Deployment transaction: `0xd88c8629a19c6189f9d9ece08f292c3bcb818ccaeef77e68ad4a7b003dab8674`
- Final chain status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- Local SHA-256: `afd51b388aafd35c97f8aaee6a4edaf4a9667bd5f2394a6b7fab46c479fcfea8`
- Chain-returned SHA-256: `afd51b388aafd35c97f8aaee6a4edaf4a9667bd5f2394a6b7fab46c479fcfea8`
- Exact source bytes: **yes**

### CourseConsumer

- Source: `contracts/course_consumer.py`
- Constructor CourseLock address: `0x7A91ce49b3755BAB0bE608FB0aB17F8F90039C9E`
- Signer/executor: `0x0d5540e0aD4B92Aa0ad4e5F1b8cD645ee1E363E7`
- Address: `0x6381F1703BFBc80ff151EB2EC3Be585aB5e3aE5C`
- Deployment transaction: `0x1ee27aeb7f648967b63c995ef6672e3dc3e86485acd4af9b3469b1952023c9ca`
- Final chain status: `FINALIZED`
- Consensus result: `MAJORITY_AGREE`
- Local SHA-256: `57ac638294a4661340304099848bba6c7ee1fbca9142c038ffc52683d8228cd6`
- Chain-returned SHA-256: `57ac638294a4661340304099848bba6c7ee1fbca9142c038ffc52683d8228cd6`
- Exact source bytes: **yes**
- `get_executor()` readback: `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7`

Explorer base: [GenLayer Explorer](https://genlayer-explorer.vercel.app). The platform’s public base was verified; no unverified deep-link format is invented here.

## Source integrity method

The final local files were read as UTF-8 bytes and hashed with SHA-256. The deployed source was retrieved with StudioNet `gen_getContractCode`, decoded from the RPC’s base64 response, and hashed with the same algorithm. Both hashes above match exactly. The final commit must retain these contract bytes; documentation-only changes do not alter deployed source.

## Public evidence namespace

The demonstration froze this mutually accepted namespace:

`https://raw.githubusercontent.com/ometere123/courselock/198b6089f1a10db196d76289aea58e12824ab74a/`

Evidence URL:

`https://raw.githubusercontent.com/ometere123/courselock/198b6089f1a10db196d76289aea58e12824ab74a/README.md`

Exact quote independently retrieved and consensus-accepted:

> CourseLock makes a previously authenticated representation and a counterparty's *pre-action* commitment part of the required enforcement history.

This proves only that the quoted public content was retrievable at an immutable GitHub commit. It does not prove source ownership, wallet-to-GitHub identity, subjective reliance, chronology, completion of an off-chain act or legal liability.

## Fully captured hardened lifecycle — Course 3

Promisor: `party_a`, `0xac3ac69dc0bde389256dd6748c75817ead9286d9`.

Counterparty: `party_b`, `0xa7eeae0e93793e3146cb14b0700251b8b0ebadfb`.

All transactions in this table were read back as `FINALIZED` with `MAJORITY_AGREE`, unless a contract-level error is explicitly stated.

| Step | Transaction and finalized readback |
|---|---|
| Course creation | `0x27bb1ecf0f6c8337ef7abd00bc7e5629b746fd58eccf51c54dc6125d1ae98fe4`; course `3`, course hash `270ddb947e63d7ebb7f3094d0de9f81d397b5d69b7ff37409729819163330e40` |
| Counterparty acceptance | `0x042081bb3e0c1ab43065ec3fb989c0da8563696c0918c7c807ecce3b0f56194b`; readback `ACTIVE` |
| Representation registration | `0xdcf988206516dfaf27b438923aed6209c3c237a673412ddeeb21444d248f6fe0`; representation `2`, hash `2e83bcb17cd46d97eb86877eaf51e2c6602a2028b9ab7862b8d9424878755a6a` |
| Reliance commitment | `0xd1780cc24aa5fe969d5b883cd76176d896f16df5e80dc56d50c7c6e6f093233d`; reliance `2`, commitment hash `4d9803420cd72616e4af968b3e533fe174f3a4d72e442be9406b48edb6dc73b4` |
| Evidence verification | `0x8b54f31eaa0856e04074174faf37576c6c3aa4f72b1518edc3c1a236e2b65737`; readback `CONFIRMED`, proof reason `VERBATIM_QUOTE_PRESENT_IN_CONTEXT_CONFIRMING_ACTION`, evidence hash `7462d8f39d3af499b20f6d8aa71a8aa8657a70049d26cceb269c0147dc41d2fe` |
| Contradictory position | `0x09c45b894b7014336ab802360a34d4ab31428f0f24a75432a46ff7d9149c6911`; attempt `5`, position hash `aaf2f9421bd2feae5f8d2bc69470b5807072e83e6e74652f81f0dbb252a720fc` |
| Contradiction assessment | `0xbe5caca2b5ac329f06c9b5fefe6d4d195d2483fa5874276a2edf6c76d91d3bc0`; readback `BLOCKED`, relation `CONTRADICTORY`, `same_action=true`, `reverses_treatment=true` |
| Consistent position | `0xc11bacffbc8113a42b3cfe6943a98c8a8b2431bad7ec15995c5d15c17936ef6b`; attempt `6`, position hash `fa6addfd498381ee30cee1d35ef50bf6d917443800ee85f1543cf0f269d93fd1` |
| Consistency assessment | `0xd574f5d08a8f256e2b5fd6a12dd8a5bef5c009b7942eed75ac5d6425d8510bfa`; readback `CLEARED`, relation `CONSISTENT`, `same_action=true`, `reverses_treatment=false` |
| Exact clearance view | `can_enforce(6, 2e83…5a6a, 4d98…73b4, fa6a…3fd1) == true` |
| Stale binding rejection | `0xba8229f12752cd38b40da1df4b092c92683565a41d4c21d466e936a76588675d`; finalized contract error `STALE_BINDING` |

## Historical protection, ambiguity and closure — Course 1

Course 1 was used as the retained-history and consumer fixture. The final readbacks were: representation `1` hash `9f37fcfe63c9c2799d21dd3cad3d6afca49976cb6f4f676dffa7c705d307c059`; reliance `1` commitment `3b8d7525951c38c4fc7fd0bc7e02f95a4b0bee471f152803bbb886860be41061`; confirmed evidence hash `12c7044961aa04af52d4ad3cb18abd3efad4f34d6b263202f5c5b7e2e42485a8`.

- Unauthorized proof attempt: `0xbafe2828ac0747d9330a68d485dd724ed4b0f479c83f649fa7e0369572d68c2f` → finalized `ONLY_RELYING_PARTY`, no proof state change.
- Valid proof: `0x314ea7ab209bc25fb42feff387f652d3cc4764a67a092a961e147270df2aaeff` → finalized `CONFIRMED`.
- Unauthorized position attempt: `0xca582d6c724ab9218822c88840dbeaaa8cc10fe95c3255aafa101222ef96d457` → finalized `ONLY_PROMISOR`.
- Contradictory position/assessment: `0xe874358b984d8e238f6ebc5a6b38192e6bb31640cc8d60e8c2ad037a40313c02` / `0xa471ecd824e8e3ba1baf2b916fa436d90f05795e631ea20db1d21d779836fd1d` → finalized `BLOCKED`; `can_enforce=false`.
- Consistent position/assessment: `0xd71ac0475c17c6ad1cccd86cdcfa0a778f8e0879ef39a3c3659b5495bb56c862` / `0xbf69916b4059d28ec79eec1e4da0bd130b52e8f9201cbef95fbaba5fd1e06611` → finalized `CLEARED`; exact `can_enforce=true` for attempt `2`.
- Non-decisive position assessment: `0xbda9343457b79dabee15a8d8800e70b62fea6652f17f8c112f346fefb2f51ee0` → finalized `UNDETERMINED / MAJORITY_DISAGREE`; attempt `4` remained `OPEN`; `can_enforce=false`.
- Withdrawal: `0xb75ac68187602d10f95a3e9893823cd02cbf050fb5507682d40bdd4a13a3bac4` → finalized; representation readback `WITHDRAWN`, prior reliance still `CONFIRMED`.
- New reliance after withdrawal: `0xdc50106533b948cbf6642aace9118444eb46d431eb2b0d145a576718518ff455` → finalized `RELIANCE_WINDOW_CLOSED`.
- Closure: `0xc3fedb6b35656ec24d2c55e6df7a37e2aec81d83ff8ee946b21bae3519ff7f0e` → finalized; course readback `CLOSED`.
- New representation after closure: `0xd1760eb973e71419d082c7beb6b5bd322435d909671b8219e7837dd6c4e8b3d4` → finalized `COURSE_NOT_ACTIVE`.

## Cross-contract consumer proofs

The consumer executor is `0x0d5540e0ad4b92aa0ad4e5f1b8cd645ee1e363e7`.

- Blocked CourseLock attempt: `0xe699f9e80d4f183deedbc92686919ba8970db48bd0124d80097ad151ba06b574` → finalized `NO_COURSELOCK_CLEARANCE`; count remained `0`.
- Cleared intent commit: `0xea68c70bba8cf42659195fb289adc3ea0b76d0441f0d4ac9bf019180ee45e0af` → finalized; payload hash `192e7eeae9bb8a0db5df80d3f34ddc7536fa24d24660364c37d781be132923e0`.
- Exact cleared execution: `0xfc5519ff9187094e285ac0d081f388efe958b27f00ab6bc42a3a1ca060476cf3` → finalized success; count became `1`.
- Exact replay: `0xaf9b5984bfd58f8fbbe5248955fc47dfd38031c00d2df5fa86e600b2d7ccbeea` → finalized `ACTION_ALREADY_EXECUTED`; count stayed `1`.
- Payload substitution: `0x49b41b76f71d8b638a32ee4e42709fbc98f43ef2d5781408bdef8346c736ad4f` → finalized `PAYLOAD_BINDING_MISMATCH`.
- Unauthorized wallet: `0x17510b96f9bc1e90b1c6cd5556acc1b985fd6addacfa38e65e6e1a086b8f0764` → finalized `ONLY_EXECUTOR`.

## Baseline preservation

The baseline commit was `251ff349e4c8ed1c73dc573e5074de88dafa5c3f`. Its pre-hardening source hashes were:

| Source | Baseline SHA-256 |
|---|---|
| `contracts/courselock.py` | `c5d06e1de41d0fc7a0982575f66fe293151b8afd90078550e2da9cfe0b1b537a` |
| `contracts/course_consumer.py` | `62ffdf651e1e5bd6b0808776e6c0afab3cc4c23424877e56a646988d5e428257` |

The baseline deployment at `0xc0c6016b1Ef9Dc9D4bEC33D651Eb5F6Eb91B8167` and baseline consumer at `0xaa8a5Cd74f6A0f82A4413AF0a8ce71Bb09DcbF90` remain historical only. They are not presented as deployments of the hardened source.
