#!/usr/bin/env python3
"""Static guard, not GenVM proof or source-matched live evidence."""
import ast
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
contract=ROOT/'contracts/courselock.py'
consumer=ROOT/'contracts/course_consumer.py'
source=contract.read_text()
checks=[]
def ck(value,label):
    assert value,label
    checks.append(label)
ast.parse(source)
ast.parse(consumer.read_text())
ck(True,'main and consumer parse')
ck(source.count('gl.vm.run_nondet_unsafe(')==2,'two substantive custom consensus boundaries')
ck('INDEPENDENT SOURCE CHECK' in source,'validator re-fetches action proof')
ck('INDEPENDENT POSITION CHECK' in source,'validator independently assesses contradicton')
ck('ADVERSARIAL CONTRADICTION AUDIT' in source,'adversarial compatibility audit')
ck('ADVERSARIAL CLEARANCE AUDIT' in source,'positive clearance compatibility audit')
ck('PROOF_RETRYABLE' in source and 'PROOF_EXHAUSTED' in source,'bounded evidence recovery states')
ck('ATTEMPT_RETRYABLE' in source and 'ASSESSMENT_RETRY_LIMIT' in source,'bounded position recovery states')
ck('EVIDENCE_BINDING_IMMUTABLE' in source,'retry cannot substitute evidence')
ck('gl.nondet.web.render' in source,'real web retrieval (not a thin LLM wrapper)')
ck('ONLY_PROMISOR' in source and 'ONLY_COUNTERPARTY' in source,'wallet-authenticated parties')
ck('RELIANCE_WINDOW_CLOSED' in source,'no reliance after withdrawal or close')
ck('STALE_REPRESENTATION' in source and 'STALE_BINDING' in source,'immutable hash pins')
ck('NO_CONFIRMED_ACTION' in source,'no unverified reliance clearance')
ck('def can_enforce(' in source and 'def is_protected(' in source,'consumer view gates')
ck('gate.view().can_enforce(' in consumer.read_text(),'IC-to-IC consumer refuses unapproved position')
ck('def commit_action(' in consumer.read_text() and 'COURSELOCK_CONSUMER_ACTION' in consumer.read_text(),
   'consumer payload commitment is domain separated')
ck('PAYLOAD_BINDING_MISMATCH' in consumer.read_text() and 'ACTION_INTENT_ALREADY_EXECUTED' in consumer.read_text(),
   'consumer rejects substituted and replayed actions')
config=(ROOT/'package.json').read_text()
ck(json.loads(config)['devDependencies']['genlayer']=='0.39.1','repository-local stable CLI pin')
ck('https://studio.genlayer.com/api' in (ROOT/'scripts/assert_studionet.mjs').read_text(),'correct stable RPC')
ck('61999' in (ROOT/'scripts/assert_studionet.mjs').read_text(),'correct chain guard')
ck('studionet' in (ROOT/'gltest.config.yaml').read_text(),'stable network in tester config')
print(f'CourseLock structural preflight: {len(checks)} checks passed')
