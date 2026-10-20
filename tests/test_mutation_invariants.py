"""Small executable mutation checks for high-value authorization invariants.

Each mutant is imported and exercised through the offline VM harness. The
tests pass only when the mutated contract violates the expected invariant and
the regression assertion detects that violation; these are not source-string
presence checks.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

import conftest as offline_conftest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://example.org/receipts/action-41'
PREFIX = 'https://example.org/receipts/'
SCOPE = 'Deliverables for contract 41.'
PROMISE = 'Deliverable 41 submitted by Friday is timely.'
ACTION = 'Customer submitted deliverable 41 on Thursday.'
QUOTE = 'Customer submitted deliverable 41 on Thursday.'
PAGE = 'Public receipt: ' + QUOTE
DENY = 'Deliverable 41 submitted Thursday is late because the deadline was Wednesday.'


def load_mutant(source: str, tmp_path, monkeypatch):
    path = tmp_path / 'courselock_mutant.py'
    path.write_text(source, encoding='utf-8')
    rt, genlayer_module = offline_conftest.build_runtime()
    monkeypatch.setitem(sys.modules, 'genlayer', genlayer_module)
    spec = importlib.util.spec_from_file_location('courselock_mutant', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rt.module = module
    rt.contract = module.CourseLock()
    return rt, module, rt.contract


def confirmed_reliance(rt, contract):
    course = contract.open_course('0xB', SCOPE, PREFIX)
    rt.sender = '0xB'
    contract.accept_course(course)
    rt.sender = '0xA'
    rep = contract.publish_representation(course, PROMISE)
    rt.sender = '0xB'
    reliance = contract.commit_reliance(
        rep, ACTION, 'because the promise was recorded.',
        contract.get_representation(rep)['hash'],
    )
    rt.pages[SOURCE] = PAGE
    rt.llm = lambda prompt: {'status': 1, 'reason': 'PUBLIC_RECEIPT_MATCH'}
    contract.prove_action(reliance, SOURCE, QUOTE)
    return course, rep, reliance


def test_mutant_that_reopens_final_proof_is_caught(tmp_path, monkeypatch):
    original = (ROOT / 'contracts' / 'courselock.py').read_text(encoding='utf-8')
    marker = 'if int(record.proof_status) not in (PROOF_UNPROVEN, PROOF_RETRYABLE):'
    assert marker in original
    mutant = original.replace(marker, 'if False:', 1)
    rt, _, contract = load_mutant(mutant, tmp_path, monkeypatch)
    _, _, reliance = confirmed_reliance(rt, contract)
    rt.llm = lambda prompt: {'status': 2, 'reason': 'NOT_SUPPORTED'}
    try:
        contract.prove_action(reliance, SOURCE, QUOTE)
    except Exception:
        pytest.fail('the terminal-proof mutant was not exercised')
    assert contract.get_reliance(reliance)['proof_status'] != 1


def test_mutant_that_allows_third_party_settlement_is_caught(tmp_path, monkeypatch):
    original = (ROOT / 'contracts' / 'courselock.py').read_text(encoding='utf-8')
    marker = 'if gl.message.sender_address not in (course.promisor, course.counterparty):'
    assert marker in original
    mutant = original.replace(marker, 'if False:', 1)
    rt, _, contract = load_mutant(mutant, tmp_path, monkeypatch)
    _, _, reliance = confirmed_reliance(rt, contract)
    record = contract.get_reliance(reliance)
    rt.sender = '0xA'
    attempt = contract.open_position(
        reliance, DENY, record['commitment_hash'], record['evidence_hash']
    )
    rt.llm = lambda prompt: (
        {'relation': 2, 'same_action': True, 'reverses_treatment': True,
         'reason': 'DEADLINE_REVERSED', 'witness': 'Friday promised; Wednesday imposed'}
        if '/ CONTRADICTORY ENFORCEMENT' in prompt
        else {'counterexample': False, 'ambiguous': False}
    )
    rt.sender = '0xC'
    try:
        contract.assess_position(attempt)
    except Exception:
        pytest.fail('the third-party-assessment mutant was not exercised')
    assert contract.get_attempt(attempt)['status'] == 2
