"""Stable GenVM Direct Mode security and lifecycle regression tests.

Requires genlayer-test==0.29.0. Run with:
  gltest direct_tests -v -s

Direct Mode executes the contract in the pinned test SDK and exercises the
leader path plus deterministic storage/authorization. The offline suite also
invokes the validator callbacks directly; hosted StudioNet is required for
full multi-validator consensus and live web retrieval.
"""
import json

import pytest

CONTRACT = 'contracts/courselock.py'
CONSUMER = 'contracts/course_consumer.py'
PREFIX = 'https://example.org/receipts/'
SOURCE = PREFIX + 'item-41'
SCOPE = 'Delivery and acceptance of item 41 under the Friday deadline.'
PROMISE = 'Item 41 delivered before Friday at 17:00 UTC will be accepted as timely.'
ACTION = 'Buyer submitted item 41 on Thursday at 14:00 UTC.'
REASON = 'Buyer acted because the Friday deadline was recorded.'
QUOTE = 'Buyer submitted item 41 on Thursday at 14:00 UTC.'
PAGE = 'Official delivery receipt for item 41: ' + QUOTE
DENY = 'Item 41 from Thursday is late; the deadline was Wednesday, not Friday.'
ALLOW = 'Item 41 submitted Thursday is timely under the Friday deadline.'
AMBIGUOUS = 'The Thursday item may be late depending on a receipt condition.'


def proof(status=1, reason='PUBLIC_RECEIPT_MATCH'):
    return json.dumps({'status': status, 'reason': reason})


def relation(relation_code=2, same=True, reverses=True):
    return json.dumps({
        'relation': relation_code,
        'same_action': same,
        'reverses_treatment': reverses,
        'reason': 'DEADLINE_CONFLICT' if relation_code == 2 else 'SAFE_NON_CONTRADICTION',
        'witness': 'Friday promised; Wednesday imposed' if relation_code == 2 else '',
    })


def mock_web(direct_vm, page=PAGE):
    direct_vm.mock_web(
        r'.*example\.org/receipts/item-41.*',
        {'status': 200, 'body': page},
    )


def mock_proof(direct_vm, status=1, page=PAGE):
    mock_web(direct_vm, page)
    direct_vm.mock_llm(r'COURSELOCK / LEADER SOURCE CHECK', proof(status))


def mock_position(direct_vm, relation_code=2, same=True, reverses=True):
    direct_vm.mock_llm(
        r'COURSELOCK / LEADER POSITION CHECK',
        relation(relation_code, same, reverses),
    )


def open_offered(direct_vm, direct_deploy, direct_bob):
    contract = direct_deploy(CONTRACT)
    try:
        from genlayer import Address
    except ModuleNotFoundError:
        # The Direct Mode loader removes the temporary SDK module after a
        # deploy until the first wrapped call executes.
        contract.get_status_dictionary()
        from genlayer import Address
    course_id = contract.open_course(Address(direct_bob), SCOPE, PREFIX)
    return contract, course_id


def open_active(direct_vm, direct_deploy, direct_bob):
    contract, course_id = open_offered(direct_vm, direct_deploy, direct_bob)
    promisor = direct_vm.sender
    direct_vm.sender = direct_bob
    contract.accept_course(course_id)
    direct_vm.sender = promisor
    return contract, course_id, promisor


def create_reliance(direct_vm, direct_deploy, direct_bob):
    contract, course_id, promisor = open_active(direct_vm, direct_deploy, direct_bob)
    rep_id = contract.publish_representation(course_id, PROMISE)
    rep = contract.get_representation(rep_id)
    direct_vm.sender = direct_bob
    reliance_id = contract.commit_reliance(rep_id, ACTION, REASON, rep['hash'])
    return contract, course_id, rep_id, reliance_id, rep, promisor


def create_confirmed_reliance(direct_vm, direct_deploy, direct_bob):
    contract, course_id, rep_id, reliance_id, rep, promisor = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    mock_proof(direct_vm)
    contract.prove_action(reliance_id, SOURCE, QUOTE)
    direct_vm.sender = promisor
    reliance = contract.get_reliance(reliance_id)
    return contract, course_id, rep_id, reliance_id, reliance, promisor


def test_course_requires_typed_nonzero_counterparty(direct_vm, direct_deploy, direct_bob):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert('BAD_COUNTERPARTY_ADDRESS'):
        contract.open_course('0x' + 'b' * 40, SCOPE, PREFIX)
    from genlayer import Address
    with direct_vm.expect_revert('ZERO_COUNTERPARTY_ADDRESS'):
        contract.open_course(Address('0x' + '0' * 40), SCOPE, PREFIX)
    contract.open_course(Address(direct_bob), SCOPE, PREFIX)


def test_only_designated_counterparty_can_accept_and_acceptance_is_one_way(
    direct_vm, direct_deploy, direct_bob, direct_charlie
):
    contract, course_id = open_offered(direct_vm, direct_deploy, direct_bob)
    with direct_vm.prank(direct_charlie):
        with direct_vm.expect_revert('ONLY_COUNTERPARTY'):
            contract.accept_course(course_id)
    with direct_vm.prank(direct_bob):
        contract.accept_course(course_id)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('COURSE_NOT_OFFERED'):
            contract.accept_course(course_id)


def test_no_representation_or_reliance_before_acceptance(direct_vm, direct_deploy, direct_bob):
    contract, course_id = open_offered(direct_vm, direct_deploy, direct_bob)
    with direct_vm.expect_revert('COURSE_NOT_ACTIVE'):
        contract.publish_representation(course_id, PROMISE)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('UNKNOWN_REPRESENTATION'):
            contract.commit_reliance(1, ACTION, REASON, '0' * 64)


def test_promisor_and_counterparty_cannot_swap_identities(
    direct_vm, direct_deploy, direct_bob, direct_charlie
):
    contract, course_id, promisor = open_active(direct_vm, direct_deploy, direct_bob)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('ONLY_PROMISOR'):
            contract.publish_representation(course_id, PROMISE)
    direct_vm.sender = promisor
    rep_id = contract.publish_representation(course_id, PROMISE)
    rep = contract.get_representation(rep_id)
    with direct_vm.prank(direct_charlie):
        with direct_vm.expect_revert('ONLY_COUNTERPARTY'):
            contract.commit_reliance(rep_id, ACTION, REASON, rep['hash'])
    with direct_vm.prank(promisor):
        with direct_vm.expect_revert('ONLY_COUNTERPARTY'):
            contract.commit_reliance(rep_id, ACTION, REASON, rep['hash'])


def test_stale_and_invalid_ids_fail_closed(direct_vm, direct_deploy, direct_bob):
    contract, course_id, _ = open_active(direct_vm, direct_deploy, direct_bob)
    with pytest.raises(Exception, match='UNKNOWN_COURSE'):
        contract.get_course(999)
    assert not contract.can_enforce(999, 'a', 'b', 'c')
    assert not contract.is_protected(999)
    rep_id = contract.publish_representation(course_id, PROMISE)
    rep = contract.get_representation(rep_id)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('STALE_REPRESENTATION'):
            contract.commit_reliance(rep_id, ACTION, REASON, '0' * 64)
        reliance_id = contract.commit_reliance(rep_id, ACTION, REASON, rep['hash'])
    assert reliance_id == 1


def test_withdrawal_blocks_new_reliance_but_preserves_prior_history(
    direct_vm, direct_deploy, direct_bob
):
    contract, _, rep_id, reliance_id, _, promisor = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    with direct_vm.prank(promisor):
        contract.withdraw_representation(rep_id)
    rep = contract.get_representation(rep_id)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('RELIANCE_WINDOW_CLOSED'):
            contract.commit_reliance(rep_id, ACTION, REASON, rep['hash'])
    assert contract.get_reliance(reliance_id)['commitment_hash']


def test_close_preserves_historical_reliance_but_stops_new_operations(
    direct_vm, direct_deploy, direct_bob
):
    contract, course_id, _, reliance_id, _, promisor = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    with direct_vm.prank(promisor):
        contract.close_course(course_id)
    assert contract.get_course(course_id)['status'] == 3
    with direct_vm.prank(promisor):
        with direct_vm.expect_revert('COURSE_NOT_ACTIVE'):
            contract.publish_representation(course_id, 'New promise')
    assert contract.get_reliance(reliance_id)['id'] == reliance_id


def test_valid_evidence_is_bound_to_exact_quote_and_url(direct_vm, direct_deploy, direct_bob):
    contract, _, _, reliance_id, _, _ = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    mock_proof(direct_vm)
    contract.prove_action(reliance_id, SOURCE, QUOTE)
    record = contract.get_reliance(reliance_id)
    assert record['proof_status'] == 1
    assert record['evidence_url'] == SOURCE
    assert record['evidence_quote'] == QUOTE
    assert len(record['evidence_hash']) == 64


@pytest.mark.parametrize('bad_url', [
    'http://example.org/receipts/item-41',
    'https://evil.example/receipts/item-41',
    'https://example.org.evil/receipts/item-41',
    'https://evil@example.org/receipts/item-41',
    'https://example.org/receipts/../private',
    'https://127.0.0.1.nip.io/receipts/item-41',
])
def test_evidence_namespace_rejects_scheme_host_and_path_confusion(
    direct_vm, direct_deploy, direct_bob, bad_url
):
    contract, _, _, reliance_id, _, _ = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    with direct_vm.expect_revert('SOURCE_OUT_OF_SCOPE'):
        contract.prove_action(reliance_id, bad_url, QUOTE)


def test_missing_quote_unreachable_and_oversized_pages_never_confirm(
    direct_vm, direct_deploy, direct_bob
):
    contract, _, _, reliance_id, _, _ = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    mock_proof(direct_vm, page='Unrelated public record')
    contract.prove_action(reliance_id, SOURCE, QUOTE)
    assert contract.get_reliance(reliance_id)['proof_status'] == 2

    direct_vm.clear_mocks()
    direct_vm.sender = direct_bob
    reliance2 = contract.commit_reliance(
        1, ACTION + ' second receipt', REASON, contract.get_representation(1)['hash']
    )
    mock_proof(direct_vm, page='x' * 13001)
    contract.prove_action(reliance2, SOURCE, QUOTE)
    assert contract.get_reliance(reliance2)['proof_status'] == 3


def test_malformed_proof_response_fails_closed(direct_vm, direct_deploy, direct_bob):
    contract, _, _, reliance_id, _, _ = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    mock_web(direct_vm)
    direct_vm.mock_llm(r'COURSELOCK / LEADER SOURCE CHECK', json.dumps({'status': 1}))
    contract.prove_action(reliance_id, SOURCE, QUOTE)
    assert contract.get_reliance(reliance_id)['proof_status'] == 3


def test_confirmed_reliance_is_required_before_position(
    direct_vm, direct_deploy, direct_bob
):
    contract, _, rep_id, reliance_id, _, promisor = create_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    rep = contract.get_representation(rep_id)
    reliance = contract.get_reliance(reliance_id)
    with direct_vm.prank(promisor):
        with direct_vm.expect_revert('NO_CONFIRMED_ACTION'):
            contract.open_position(
                reliance_id, DENY, reliance['commitment_hash'], reliance['evidence_hash']
            )
    assert rep['hash'] == reliance['representation_hash']


def test_contradictory_position_blocks_and_cannot_clear_consumer(
    direct_vm, direct_deploy, direct_bob
):
    contract, _, _, reliance_id, reliance, _ = create_confirmed_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    attempt_id = contract.open_position(
        reliance_id, DENY, reliance['commitment_hash'], reliance['evidence_hash']
    )
    mock_position(direct_vm, relation_code=2, same=True, reverses=True)
    contract.assess_position(attempt_id)
    attempt = contract.get_attempt(attempt_id)
    assert attempt['status'] == 2
    assert contract.is_protected(attempt_id)
    assert not contract.can_enforce(
        attempt_id, reliance['representation_hash'], reliance['commitment_hash'],
        attempt['position_hash'],
    )


def test_consistent_position_clears_only_exact_binding(
    direct_vm, direct_deploy, direct_bob
):
    contract, _, _, reliance_id, reliance, _ = create_confirmed_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    attempt_id = contract.open_position(
        reliance_id, ALLOW, reliance['commitment_hash'], reliance['evidence_hash']
    )
    mock_position(direct_vm, relation_code=1, same=True, reverses=False)
    contract.assess_position(attempt_id)
    attempt = contract.get_attempt(attempt_id)
    assert attempt['status'] == 1
    assert contract.can_enforce(
        attempt_id, reliance['representation_hash'], reliance['commitment_hash'],
        attempt['position_hash'],
    )
    assert not contract.can_enforce(attempt_id, '0' * 64, reliance['commitment_hash'], attempt['position_hash'])
    assert not contract.can_enforce(attempt_id, reliance['representation_hash'], '0' * 64, attempt['position_hash'])
    assert not contract.can_enforce(attempt_id, reliance['representation_hash'], reliance['commitment_hash'], '0' * 64)


@pytest.mark.parametrize('relation_code,same,reverses', [
    (3, False, False),
    (4, False, False),
    (2, False, False),
    (1, True, True),
])
def test_unrelated_ambiguous_or_incomplete_relation_never_clears(
    direct_vm, direct_deploy, direct_bob, relation_code, same, reverses
):
    contract, _, _, reliance_id, reliance, _ = create_confirmed_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    attempt_id = contract.open_position(
        reliance_id, AMBIGUOUS, reliance['commitment_hash'], reliance['evidence_hash']
    )
    mock_position(direct_vm, relation_code, same, reverses)
    contract.assess_position(attempt_id)
    assert contract.get_attempt(attempt_id)['status'] == 3
    assert not contract.can_enforce(
        attempt_id, reliance['representation_hash'], reliance['commitment_hash'],
        contract.get_attempt(attempt_id)['position_hash'],
    )


def test_assessment_is_final_and_replay_is_rejected(direct_vm, direct_deploy, direct_bob):
    contract, _, _, reliance_id, reliance, _ = create_confirmed_reliance(
        direct_vm, direct_deploy, direct_bob
    )
    attempt_id = contract.open_position(
        reliance_id, ALLOW, reliance['commitment_hash'], reliance['evidence_hash']
    )
    mock_position(direct_vm, relation_code=1, same=True, reverses=False)
    contract.assess_position(attempt_id)
    with direct_vm.expect_revert('ATTEMPT_ALREADY_ASSESSED'):
        contract.assess_position(attempt_id)


def test_consumer_typed_constructor_hash_validation_and_executor_gate(
    direct_vm, direct_deploy, direct_charlie
):
    consumer = direct_deploy(CONSUMER, direct_vm.sender)
    assert consumer.get_count() == 0
    with direct_vm.prank(direct_charlie):
        with direct_vm.expect_revert('ONLY_EXECUTOR'):
            consumer.execute(1, '0' * 64, '0' * 64, '0' * 64, 'b' * 64)
    with direct_vm.expect_revert('BAD_REPRESENTATION_HASH'):
        consumer.execute(1, 'z' * 64, '0' * 64, '0' * 64, 'a' * 64)


def test_status_dictionary_is_stable(direct_vm, direct_deploy, direct_bob):
    contract = direct_deploy(CONTRACT)
    status = contract.get_status_dictionary()
    assert status['course'] == {'OFFERED': 1, 'ACTIVE': 2, 'CLOSED': 3}
    assert status['proof']['CONFIRMED'] == 1
    assert status['relation']['AMBIGUOUS'] == 4
    assert status['attempt']['UNRESOLVED'] == 3
