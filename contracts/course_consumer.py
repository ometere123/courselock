# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Tiny opt-in enforcement gate: never execute on an unresolved CourseLock position.

Deploy separately for the cross-IC StudioNet proof. No money transfer is implied.
"""
from genlayer import *
from dataclasses import dataclass

HASH_LENGTH = 64
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

class CourseConsumer(gl.Contract):
    course_lock_address: Address
    executor: Address
    executions: TreeMap[str, Execution]
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

    @gl.public.write
    def execute(self, attempt_id: u256, representation_hash: str,
                commitment_hash: str, position_hash: str, action_id: str) -> None:
        if gl.message.sender_address != self.executor:
            raise gl.vm.UserError('ONLY_EXECUTOR')
        representation_hash = self._require_hash(representation_hash, 'REPRESENTATION')
        commitment_hash = self._require_hash(commitment_hash, 'COMMITMENT')
        position_hash = self._require_hash(position_hash, 'POSITION')
        if len(action_id) != 64 or any(c not in '0123456789abcdef' for c in action_id):
            raise gl.vm.UserError('ACTION_ID_MUST_BE_64_HEX')
        if self.executions.get(action_id) is not None:
            raise gl.vm.UserError('ACTION_ALREADY_EXECUTED')
        gate = ICourseLock(self.course_lock_address)
        if not gate.view().can_enforce(attempt_id, representation_hash, commitment_hash, position_hash):
            raise gl.vm.UserError('NO_COURSELOCK_CLEARANCE')
        self.executions[action_id] = Execution(attempt_id=attempt_id, action_id=action_id,
                                               position_hash=position_hash,
                                               caller=gl.message.sender_address)
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
