# Deployment evidence — pending final StudioNet run

**Target**: stable `studionet`, chain ID **61999**, RPC `https://studio.genlayer.com/api`. **Local CLI `genlayer@0.39.1` only**. Never use global `0.40.0rc2` or the release-candidate preview network.

## Prepared commands

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests -q
python scripts/preflight.py
gltest direct_tests -v -s
npm install
npm run cli:version
node scripts/assert_studionet.mjs
npm run deploy:guarded
```

`deploy:guarded` prompts for explicit `DEPLOY-61999` confirmation and deploys the primary contract only. To deploy the optional integration consumer once the primary is finalized, use the **local binary**, after re-running the network guard:

```bash
./node_modules/.bin/genlayer deploy --contract contracts/course_consumer.py --rpc https://studio.genlayer.com/api --args <FINALIZED_COURSELOCK_ADDRESS>
```

On Windows use `npx --no-install genlayer` or `.\\node_modules\\.bin\\genlayer.cmd` explicitly.

## Source matching

Run `python scripts/hash_manifest.py` to print SHA-256 digests for primary/consumer contracts and repository files. Record chain-displayed source/code and compare with exact committed main branch. Never infer equivalence from contract name.

## Live evidence template (populate ONLY from real network receipts)

- Head commit: **PENDING**
- Network/chain readback: **PENDING**
- Primary contract address: **PENDING**
- Primary deploy tx + finality: **PENDING**
- Consumer contract address: **PENDING**
- Consumer deploy tx + finality: **PENDING**
- Authenticated two-party course/representation: **PENDING**
- Pre-action reliance and independently re-fetched proof: **PENDING**
- Contradictory BLOCKED position: **PENDING**
- Consistent CLEARED position: **PENDING**
- Ambiguous/hostile negative proof: **PENDING**
- Consumer BLOCKED negative and CLEARED positive + replay rejection: **PENDING**
- Full Direct Mode suite + CI green: **PENDING**
- Source SHA-256 and on-chain code parity: **PENDING**

No fabricated tx hashes or explorer URLs belong in this document.
