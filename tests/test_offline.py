"""Deterministic plus validator callback tests using the explicit offline mock."""
import pytest

SOURCE='https://example.org/receipts/action-41'
PREFIX='https://example.org/receipts/'
SCOPE='Deliverables for contract 41; applicable delivery deadline and acceptance conditions.'
PROMISE='Deliverables submitted by Friday at 17:00 UTC count as timely.'
ACTION='Customer submitted deliverable 41 on Thursday at 14:00 UTC.'
EVIDENCE='Signed receipt states customer submitted deliverable 41 Thursday at 14:00 UTC.'
DENY='Deliverable 41 submitted Thursday at 14:00 UTC is late because the deadline was Wednesday.'
ALLOW='Deliverable 41 submitted Thursday at 14:00 UTC is timely under the Friday deadline.'


def proof(st=1,reason='DELIVERY_CONFIRMED'):
    return {'status':st,'reason':reason}

def rel(relation=2,same=True,reverses=True,reason='DEADLINE_REVERSED',witness='Friday promised but Wednesday imposed'):
    return {'relation':relation,'same_action':same,'reverses_treatment':reverses,'reason':reason,'witness':witness}

def position_result(value):
    return dict(value, retryable=False)

def mock_llm(rt,p=1,r=2):
    def run(prompt):
        if '/ SOURCE-BACKED ACTION CHECK' in prompt:return proof(p)
        if 'ADVERSARIAL CLEARANCE AUDIT' in prompt:
            return {'counterexample':False,'ambiguous':False}
        if '/ CONTRADICTORY ENFORCEMENT' in prompt:
            return rel(r,True,r==2,witness='deadline shifted' if r==2 else '')
        if 'ADVERSARIAL CONTRADICTION AUDIT' in prompt:
            return {'counterexample':False,'ambiguous':False}
        raise AssertionError('Unexpected prompt')
    rt.llm=run


def setup(rt):
    c=rt.contract
    course_id=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB'
    c.accept_course(course_id)
    rt.sender='0xA'
    rep_id=c.publish_representation(course_id,PROMISE)
    rt.sender='0xB'
    rep_hash=c.get_representation(rep_id)['hash']
    rid=c.commit_reliance(rep_id,ACTION,'I act because Friday submissions are timely.',rep_hash)
    rt.pages[SOURCE]='Case 41 public receipt: '+EVIDENCE
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    rt.sender='0xA'
    evidence=c.get_reliance(rid)
    aid=c.open_position(rid,DENY,evidence['commitment_hash'],evidence['evidence_hash'])
    return course_id,rep_id,rid,aid


def test_complete_contradiction_blocks(harness):
    rt=harness;c=rt.contract
    _,rep,rid,aid=setup(rt)
    assert c.get_reliance(rid)['proof_status']==1
    c.assess_position(aid)
    assert c.get_attempt(aid)['status']==2
    assert c.is_protected(aid)
    r=c.get_reliance(rid);a=c.get_attempt(aid)
    assert not c.can_enforce(aid,r['representation_hash'],r['commitment_hash'],a['position_hash'])


def test_consistent_position_clears(harness):
    rt=harness;c=rt.contract
    _,rep,rid,_=setup(rt)
    r=c.get_reliance(rid)
    aid=c.open_position(rid,ALLOW,r['commitment_hash'],r['evidence_hash'])
    mock_llm(rt,r=1)
    c.assess_position(aid)
    a=c.get_attempt(aid)
    assert a['status']==1
    assert c.can_enforce(aid,r['representation_hash'],r['commitment_hash'],a['position_hash'])
    assert not c.can_enforce(aid,r['representation_hash'],r['commitment_hash'],'bad_hash')


def test_no_clearance_before_consensus(harness):
    rt=harness;c=rt.contract
    _,_,rid,aid=setup(rt)
    r=c.get_reliance(rid);a=c.get_attempt(aid)
    assert not c.can_enforce(aid,r['representation_hash'],r['commitment_hash'],a['position_hash'])
    assert not c.is_protected(aid)


def test_direct_reassessment_disallowed(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    with pytest.raises(Exception,match='ATTEMPT_ALREADY_ASSESSED'):
        c.assess_position(aid)

@pytest.mark.parametrize('relation,same,reverses',[(3,False,False),(4,False,False),(2,False,False)])
def test_unrelated_and_ambiguous_fail_closed(harness,relation,same,reverses):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    rt.llm=lambda p: rel(relation,same,reverses,witness='' if relation!=2 else 'x')
    c.assess_position(aid)
    assert c.get_attempt(aid)['status'] in (3, 4)


def test_party_must_accept(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    with pytest.raises(Exception,match='COURSE_NOT_ACTIVE'):
        c.publish_representation(course,PROMISE)
    with pytest.raises(Exception,match='ONLY_COUNTERPARTY'):
        c.accept_course(course)


def test_representation_only_promisor(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    with pytest.raises(Exception,match='ONLY_PROMISOR'):
        c.publish_representation(course,PROMISE)


def test_reliance_only_counterparty(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    with pytest.raises(Exception,match='ONLY_COUNTERPARTY'):
        c.commit_reliance(rep,ACTION,'trust',c.get_representation(rep)['hash'])


def test_bad_hash_rejected(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB'
    with pytest.raises(Exception,match='STALE_REPRESENTATION'):
        c.commit_reliance(rep,ACTION,'because','0'*64)


def test_withdrawal_only_blocks_new_reliance(harness):
    rt=harness;c=rt.contract
    _,rep,rid,aid=setup(rt)
    c.withdraw_representation(rep)
    rt.sender='0xB'
    with pytest.raises(Exception,match='RELIANCE_WINDOW_CLOSED'):
        c.commit_reliance(rep,ACTION,'more',c.get_representation(rep)['hash'])
    rt.sender='0xA'
    c.assess_position(aid)
    assert c.is_protected(aid)


def test_closed_course_keeps_prior_reliance_alive(harness):
    rt=harness;c=rt.contract
    course,rep,rid,aid=setup(rt)
    c.close_course(course)
    c.assess_position(aid)
    assert c.is_protected(aid)
    with pytest.raises(Exception,match='COURSE_NOT_ACTIVE'):
        c.publish_representation(course,'Another promise')


def test_proof_failure_not_confirmed(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB'
    rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    assert c.get_reliance(rid)['proof_status']==4
    rt.sender='0xA';r=c.get_reliance(rid)
    with pytest.raises(Exception,match='NO_CONFIRMED_ACTION'):
        c.open_position(rid,DENY,r['commitment_hash'],r['evidence_hash'])


def test_transient_proof_failure_is_retryable_and_recovers_without_rebinding(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB';rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    first=c.get_reliance(rid)
    assert first['proof_status']==4
    assert first['proof_attempts']==1
    assert len(first['proof_history'])==1
    rt.pages[SOURCE]='Case 41 public receipt: '+EVIDENCE
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    second=c.get_reliance(rid)
    assert second['proof_status']==1
    assert second['proof_attempts']==2
    assert len(second['proof_history'])==2
    assert second['commitment_hash']==first['commitment_hash']


def test_retry_cannot_substitute_evidence_or_actor(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB';rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    rt.sender='0xA'
    with pytest.raises(Exception,match='ONLY_RELYING_PARTY'):
        c.prove_action(rid,SOURCE,EVIDENCE)
    rt.sender='0xB'
    with pytest.raises(Exception,match='EVIDENCE_BINDING_IMMUTABLE'):
        c.prove_action(rid,SOURCE,'substituted quote')


def test_retry_limit_exhausts_without_clearance(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB';rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    mock_llm(rt)
    for _ in range(3):
        c.prove_action(rid,SOURCE,EVIDENCE)
    record=c.get_reliance(rid)
    assert record['proof_status']==5
    assert record['proof_attempts']==3
    assert len(record['proof_history'])==3
    with pytest.raises(Exception,match='PROOF_ALREADY_ATTEMPTED'):
        c.prove_action(rid,SOURCE,EVIDENCE)


def test_semantic_inconclusive_proof_remains_terminal(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB';rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    rt.pages[SOURCE]='Case 41 public receipt: '+EVIDENCE
    mock_llm(rt,p=3)
    c.prove_action(rid,SOURCE,EVIDENCE)
    assert c.get_reliance(rid)['proof_status']==3
    with pytest.raises(Exception,match='PROOF_ALREADY_ATTEMPTED'):
        c.prove_action(rid,SOURCE,EVIDENCE)


def test_proof_quote_absent_rejected(harness):
    rt=harness;c=rt.contract
    course=c.open_course('0xB',SCOPE,PREFIX)
    rt.sender='0xB';c.accept_course(course)
    rt.sender='0xA';rep=c.publish_representation(course,PROMISE)
    rt.sender='0xB';rid=c.commit_reliance(rep,ACTION,'because',c.get_representation(rep)['hash'])
    rt.pages[SOURCE]='A wholly unrelated record'
    mock_llm(rt)
    c.prove_action(rid,SOURCE,EVIDENCE)
    assert c.get_reliance(rid)['proof_status']==2


def test_wrong_source_prefix_rejected_before_fetch(harness):
    rt=harness;c=rt.contract
    _,rep,rid,aid=setup(rt)
    before=rt.web_read_count
    rt.sender='0xB'
    with pytest.raises(Exception,match='PROOF_ALREADY_ATTEMPTED'):
        c.prove_action(rid,'https://evil.example/org',EVIDENCE)
    assert rt.web_read_count==before


def test_stale_evidence_hash_rejected(harness):
    rt=harness;c=rt.contract
    _,_,rid,_=setup(rt)
    r=c.get_reliance(rid)
    with pytest.raises(Exception,match='STALE_BINDING'):
        c.open_position(rid,ALLOW,r['commitment_hash'],'fake')


def test_non_promisor_cannot_write_position(harness):
    rt=harness;c=rt.contract
    _,_,rid,_=setup(rt)
    r=c.get_reliance(rid)
    rt.sender='0xB'
    with pytest.raises(Exception,match='ONLY_PROMISOR'):
        c.open_position(rid,ALLOW,r['commitment_hash'],r['evidence_hash'])


def test_proof_leader_validator_disagreement(harness):
    rt=harness;c=rt.contract
    setup(rt)
    rt.validation # last validation = proof
    assert rt.validation is not None


def test_proof_malicious_leader_disagrees(harness):
    rt=harness;c=rt.contract
    setup(rt)
    # Rebuild explicit independent proof comparison at the same frozen source.
    rt.llm=lambda prompt: proof(2)
    assert rt.validation(rt.module.gl.vm.Return(proof(1))) is False


def test_proof_validator_accepts_matching_independent_read(harness):
    rt=harness;c=rt.contract
    setup(rt)
    rt.llm=lambda prompt: proof(1)
    assert rt.validation(rt.module.gl.vm.Return(proof(1))) is True


def test_proof_validator_rejects_leader_confirmation_when_source_is_unavailable(harness):
    rt=harness;c=rt.contract
    setup(rt)
    rt.pages.pop(SOURCE)
    rt.llm=lambda prompt: proof(1)
    assert rt.validation(rt.module.gl.vm.Return(proof(1))) is False


def test_position_leader_validator_disagreement(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    rt.llm=lambda prompt: rel(1,same=True,reverses=False,witness='')
    assert rt.validation(rt.module.gl.vm.Return(rel(2))) is False


def test_position_validator_adversarial_veto(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    def recheck(prompt):
        if 'ADVERSARIAL CONTRADICTION AUDIT' in prompt:
            return {'counterexample':True,'ambiguous':False}
        return rel(2)
    rt.llm=recheck
    assert rt.validation(rt.module.gl.vm.Return(rel(2))) is False


def test_position_validator_positive_clearance_audit_veto(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    def recheck(prompt):
        if 'ADVERSARIAL CLEARANCE AUDIT' in prompt:
            return {'counterexample':True,'ambiguous':False}
        return rel(1,same=True,reverses=False,witness='')
    rt.llm=recheck
    assert rt.validation(rt.module.gl.vm.Return(position_result(rel(1,same=True,reverses=False,witness='')))) is False


def test_position_validator_positive_clearance_audit_accepts_only_clean_result(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    def recheck(prompt):
        if 'ADVERSARIAL CLEARANCE AUDIT' in prompt:
            return {'counterexample':False,'ambiguous':False}
        return rel(1,same=True,reverses=False,witness='')
    rt.llm=recheck
    assert rt.validation(rt.module.gl.vm.Return(position_result(rel(1,same=True,reverses=False,witness='')))) is True


def test_third_party_cannot_grief_open_assessment_and_party_can_recover(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    rt.sender='0xC'
    with pytest.raises(Exception,match='NOT_PARTY'):
        c.assess_position(aid)
    rt.sender='0xA'
    def unavailable(prompt):
        raise IOError('temporary provider failure')
    rt.llm=unavailable
    c.assess_position(aid)
    assert c.get_attempt(aid)['status']==4
    mock_llm(rt,r=1)
    c.assess_position(aid)
    assert c.get_attempt(aid)['status']==1


def test_assessment_retry_limit_is_bounded_and_not_clearance(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    def unavailable(prompt):
        raise IOError('temporary provider failure')
    rt.llm=unavailable
    for _ in range(3):
        c.assess_position(aid)
    attempt=c.get_attempt(aid)
    assert attempt['status']==3
    assert attempt['reason']=='ASSESSMENT_RETRY_LIMIT_EXHAUSTED'
    assert attempt['assessment_attempts']==3
    assert len(attempt['assessment_history'])==3
    with pytest.raises(Exception,match='ATTEMPT_ALREADY_ASSESSED'):
        c.assess_position(aid)


def test_position_validator_adversarial_pass(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    mock_llm(rt)
    assert rt.validation(rt.module.gl.vm.Return(position_result(rel(2)))) is True


def test_inject_wrong_schema_rejected(harness):
    rt=harness;c=rt.contract
    *_,aid=setup(rt)
    c.assess_position(aid)
    mock_llm(rt)
    assert not rt.validation(rt.module.gl.vm.Return({'relation':2,'same_action':True}))


def test_safety_source(harness):
    m=harness.module
    assert m.safe_prefix('https://example.org/receipts/')
    assert not m.safe_prefix('http://example.org/receipts/')
    assert not m.safe_prefix('https://localhost/x/')
    assert not m.safe_prefix('https://evil@e.com/receipts/')
    assert not m.safe_prefix('https://e.com?secret')
    assert not m.matches_prefix('https://example.org.evil.com/receipts/',PREFIX)


def test_missing_fields_are_not_consensus_approvals(harness):
    assert not harness.module.proof_shape({'status':True,'reason':'yes'})
    assert not harness.module.relation_shape({'relation':2,'same_action':True,'reverses_treatment':True,'witness':'hi','reason':''})
    assert not harness.module.relation_shape({'relation':2,'same_action':False,'reverses_treatment':True,'witness':'hi','reason':'X'})


def test_read_only_unknown_can_enforce_false(harness):
    c=harness.contract
    assert not c.can_enforce(999,'a','b','c')
    assert not c.is_protected(999)


def test_evidence_quote_roundtrip(harness):
    rt=harness;c=rt.contract
    _,_,rid,_=setup(rt)
    r=c.get_reliance(rid)
    assert r['evidence_quote']==EVIDENCE
    assert r['evidence_url']==SOURCE
    assert len(r['evidence_hash'])==64


def test_proof_attempt_immutable(harness):
    rt=harness;c=rt.contract
    _,_,rid,_=setup(rt)
    rt.sender='0xB'
    with pytest.raises(Exception,match='PROOF_ALREADY_ATTEMPTED'):
        c.prove_action(rid,SOURCE,EVIDENCE)


def test_representation_cannot_be_retracted_by_third_party(harness):
    rt=harness;c=rt.contract
    _,rep,_,_=setup(rt)
    rt.sender='0xC'
    with pytest.raises(Exception,match='ONLY_PROMISOR'):
        c.withdraw_representation(rep)


def test_multiple_positions_independent(harness):
    rt=harness;c=rt.contract
    _,_,rid,aid=setup(rt)
    r=c.get_reliance(rid)
    aid2=c.open_position(rid,ALLOW,r['commitment_hash'],r['evidence_hash'])
    mock_llm(rt)
    c.assess_position(aid)
    mock_llm(rt,r=1)
    c.assess_position(aid2)
    assert c.get_attempt(aid)['status']==2
    assert c.get_attempt(aid2)['status']==1
