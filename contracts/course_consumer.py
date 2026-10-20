# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Tiny opt-in enforcement gate: never execute on an unresolved CourseLock position.

Deploy separately for the cross-IC StudioNet proof. No money transfer is implied.
"""
from genlayer import *
from dataclasses import dataclass
import json

HASH_LENGTH = 64
MAX_PAYLOAD = 1400
ZERO_ADDRESS = '0x' + ('0' * 40)

@gl.contract_interface
class ICourseLock:
    class View:
        def can_enforce(self, attempt_id: u256, expected_representation_hash: str,
                        expected_commitment_hash: str, expected_position_hash: str) -> bool: ...

@allow_storage
@dataclass
class Execution:
    attempt_id: u256
    action_id: str
    position_hash: str
    caller: Address
    payload_hash: str

@allow_storage
@dataclass
class ActionIntent:
    attempt_id: u256
    representation_hash: str
    commitment_hash: str
    position_hash: str
    payload_hash: str
    committed_by: Address
    executed: bool

class CourseConsumer(gl.Contract):
    course_lock_address: Address
    executor: Address
    executions: TreeMap[str, Execution]
    action_intents: TreeMap[u256, ActionIntent]
    count: u256

    def __init__(self, course_lock_address: Address):
        if isinstance(course_lock_address, bytes):
            try:
                course_lock_address = Address(course_lock_address)
            except Exception:
                raise gl.vm.UserError('BAD_COURSELOCK_ADDRESS')
        if not isinstance(course_lock_address, Address):
            raise gl.vm.UserError('BAD_COURSELOCK_ADDRESS')
        if str(course_lock_address).lower() == ZERO_ADDRESS:
            raise gl.vm.UserError('ZERO_COURSELOCK_ADDRESS')
        self.course_lock_address = course_lock_address
        self.executor = gl.message.sender_address
        self.count = u256(0)

    def _require_hash(self, value: str, label: str) -> str:
        if (not isinstance(value, str) or len(value) != HASH_LENGTH
                or any(c not in '0123456789abcdef' for c in value)):
            raise gl.vm.UserError('BAD_' + label + '_HASH')
        return value

    def _require_payload(self, payload: str) -> str:
        if (not isinstance(payload, str) or len(payload.strip()) == 0
                or len(payload) > MAX_PAYLOAD):
            raise gl.vm.UserError('BAD_ACTION_PAYLOAD')
        return payload.strip()

    def _payload_hash(self, attempt_id: u256, representation_hash: str,
                      commitment_hash: str, position_hash: str,
                      payload: str) -> str:
        value = json.dumps({
            'domain': 'COURSELOCK_CONSUMER_ACTION',
            'payload': {
                'attempt_id': int(attempt_id),
                'representation_hash': representation_hash,
                'commitment_hash': commitment_hash,
                'position_hash': position_hash,
                'payload': payload,
            },
        }, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        return Keccak256(value.encode('utf-8')).hexdigest()

    def _require_clearance(self, attempt_id: u256, representation_hash: str,
                           commitment_hash: str, position_hash: str) -> None:
        gate = ICourseLock(self.course_lock_address)
        if not gate.view().can_enforce(attempt_id, representation_hash,
                                       commitment_hash, position_hash):
            raise gl.vm.UserError('NO_COURSELOCK_CLEARANCE')

    @gl.public.write
    def commit_action(self, attempt_id: u256, representation_hash: str,
                      commitment_hash: str, position_hash: str,
                      payload: str) -> str:
        if gl.message.sender_address != self.executor:
            raise gl.vm.UserError('ONLY_EXECUTOR')
        representation_hash = self._require_hash(representation_hash, 'REPRESENTATION')
        commitment_hash = self._require_hash(commitment_hash, 'COMMITMENT')
        position_hash = self._require_hash(position_hash, 'POSITION')
        payload = self._require_payload(payload)
        if self.action_intents.get(attempt_id) is not None:
            raise gl.vm.UserError('ACTION_INTENT_ALREADY_COMMITTED')
        self._require_clearance(attempt_id, representation_hash, commitment_hash, position_hash)
        payload_hash = self._payload_hash(attempt_id, representation_hash,
                                          commitment_hash, position_hash, payload)
        self.action_intents[attempt_id] = ActionIntent(
            attempt_id=attempt_id,
            representation_hash=representation_hash,
            commitment_hash=commitment_hash,
            position_hash=position_hash,
            payload_hash=payload_hash,
            committed_by=gl.message.sender_address,
            executed=False,
        )
        return payload_hash

    @gl.public.write
    def execute(self, attempt_id: u256, representation_hash: str,
                commitment_hash: str, position_hash: str, payload: str,
                payload_hash: str, action_id: str) -> None:
        if gl.message.sender_address != self.executor:
            raise gl.vm.UserError('ONLY_EXECUTOR')
        representation_hash = self._require_hash(representation_hash, 'REPRESENTATION')
        commitment_hash = self._require_hash(commitment_hash, 'COMMITMENT')
        position_hash = self._require_hash(position_hash, 'POSITION')
        payload = self._require_payload(payload)
        payload_hash = self._require_hash(payload_hash, 'PAYLOAD')
        if (not isinstance(action_id, str) or len(action_id) != 64
                or any(c not in '0123456789abcdef' for c in action_id)):
            raise gl.vm.UserError('ACTION_ID_MUST_BE_64_HEX')
        if self.executions.get(action_id) is not None:
            raise gl.vm.UserError('ACTION_ALREADY_EXECUTED')
        intent = self.action_intents.get(attempt_id)
        if intent is None:
            raise gl.vm.UserError('ACTION_INTENT_REQUIRED')
        if intent.committed_by != gl.message.sender_address:
            raise gl.vm.UserError('ACTION_INTENT_ACTOR_MISMATCH')
        if (intent.representation_hash != representation_hash
                or intent.commitment_hash != commitment_hash
                or intent.position_hash != position_hash):
            raise gl.vm.UserError('ACTION_BINDING_MISMATCH')
        expected_payload_hash = self._payload_hash(
            attempt_id, representation_hash, commitment_hash, position_hash, payload)
        if payload_hash != expected_payload_hash or intent.payload_hash != payload_hash:
            raise gl.vm.UserError('PAYLOAD_BINDING_MISMATCH')
        if intent.executed:
            raise gl.vm.UserError('ACTION_INTENT_ALREADY_EXECUTED')
        self._require_clearance(attempt_id, representation_hash, commitment_hash, position_hash)
        intent.executed = True
        self.executions[action_id] = Execution(attempt_id=attempt_id, action_id=action_id,
                                               position_hash=position_hash,
                                               caller=gl.message.sender_address,
                                               payload_hash=payload_hash)
        self.count = u256(int(self.count)+1)

    @gl.public.view
    def was_executed(self, action_id: str) -> bool:
        return self.executions.get(action_id) is not None

    @gl.public.view
    def get_count(self) -> u256:
        return self.count

    @gl.public.view
    def get_executor(self) -> Address:
        return self.executor

    @gl.public.view
    def get_action_intent(self, attempt_id: u256) -> dict:
        intent = self.action_intents.get(attempt_id)
        if intent is None:
            raise gl.vm.UserError('UNKNOWN_ACTION_INTENT')
        return {
            'attempt_id': int(intent.attempt_id),
            'representation_hash': str(intent.representation_hash),
            'commitment_hash': str(intent.commitment_hash),
            'position_hash': str(intent.position_hash),
            'payload_hash': str(intent.payload_hash),
            'committed_by': str(intent.committed_by),
            'executed': bool(intent.executed),
        }
