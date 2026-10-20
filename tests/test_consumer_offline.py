"""Consumer action-binding tests with an explicit cross-contract view stub.

The stub models only the typed CourseLock view result. It is not a live
cross-contract or StudioNet test; the real cross-contract proof is recorded
separately from finalized StudioNet transactions.
"""
import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HASH = 'a' * 64
COMMITMENT = 'b' * 64
POSITION = 'c' * 64
PAYLOAD = '{"operation":"release","amount":0}'


@pytest.fixture
def consumer_module(harness):
    spec = importlib.util.spec_from_file_location(
        'course_consumer_tested', ROOT / 'contracts' / 'course_consumer.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def consumer_env(harness, consumer_module):
    rt = harness

    class View:
        def can_enforce(self, attempt_id, representation_hash,
                        commitment_hash, position_hash):
            return (rt.consumer_gate and attempt_id == 7
                    and representation_hash == HASH
                    and commitment_hash == COMMITMENT
                    and position_hash == POSITION)

    class Gate:
        def __init__(self, address):
            self.address = address

        def view(self):
            return View()

    consumer_module.ICourseLock = Gate
    rt.consumer_gate = True
    consumer = consumer_module.CourseConsumer('0xC')
    return rt, consumer


def test_blocked_or_unknown_course_lock_never_commits_action(consumer_env):
    rt, consumer = consumer_env
    rt.consumer_gate = False
    with pytest.raises(Exception, match='NO_COURSELOCK_CLEARANCE'):
        consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
    assert consumer.get_count() == 0


def test_exact_payload_commit_and_execute_is_single_use(consumer_env):
    rt, consumer = consumer_env
    payload_hash = consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
    intent = consumer.get_action_intent(7)
    assert intent['payload_hash'] == payload_hash
    assert intent['executed'] is False
    action_id = 'd' * 64
    consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, payload_hash, action_id)
    assert consumer.get_count() == 1
    assert consumer.was_executed(action_id)
    assert consumer.get_action_intent(7)['executed'] is True
    with pytest.raises(Exception, match='ACTION_ALREADY_EXECUTED'):
        consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, payload_hash, action_id)
    with pytest.raises(Exception, match='ACTION_INTENT_ALREADY_EXECUTED'):
        consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, payload_hash, 'e' * 64)


def test_payload_and_course_lock_hash_substitution_is_rejected(consumer_env):
    rt, consumer = consumer_env
    payload_hash = consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
    with pytest.raises(Exception, match='PAYLOAD_BINDING_MISMATCH'):
        consumer.execute(7, HASH, COMMITMENT, POSITION,
                         '{"operation":"different"}', payload_hash, 'd' * 64)
    with pytest.raises(Exception, match='ACTION_BINDING_MISMATCH'):
        consumer.execute(7, 'f' * 64, COMMITMENT, POSITION,
                         PAYLOAD, payload_hash, 'e' * 64)
    with pytest.raises(Exception, match='ACTION_INTENT_REQUIRED'):
        consumer.execute(8, HASH, COMMITMENT, POSITION,
                         PAYLOAD, payload_hash, 'f' * 64)


def test_consumer_executor_authentication_and_hash_validation(consumer_env):
    rt, consumer = consumer_env
    rt.sender = '0xB'
    with pytest.raises(Exception, match='ONLY_EXECUTOR'):
        consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
    with pytest.raises(Exception, match='ONLY_EXECUTOR'):
        consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, HASH, 'd' * 64)
    rt.sender = '0xA'
    with pytest.raises(Exception, match='BAD_PAYLOAD_HASH'):
        consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, 'Z' * 64, 'd' * 64)
    with pytest.raises(Exception, match='ACTION_ID_MUST_BE_64_HEX'):
        consumer.execute(7, HASH, COMMITMENT, POSITION, PAYLOAD, HASH, 7)


def test_consumer_payload_hash_is_domain_separated_and_bounded(consumer_env):
    rt, consumer = consumer_env
    with pytest.raises(Exception, match='BAD_ACTION_PAYLOAD'):
        consumer.commit_action(7, HASH, COMMITMENT, POSITION, '')
    with pytest.raises(Exception, match='BAD_ACTION_PAYLOAD'):
        consumer.commit_action(7, HASH, COMMITMENT, POSITION, 'x' * 1401)
    first = consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
    assert first != consumer._payload_hash(7, COMMITMENT, HASH, POSITION, PAYLOAD)
    with pytest.raises(Exception, match='ACTION_INTENT_ALREADY_COMMITTED'):
        consumer.commit_action(7, HASH, COMMITMENT, POSITION, PAYLOAD)
