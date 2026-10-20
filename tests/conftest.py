"""A labelled offline GenVM mock for deterministic and validator-callback tests.

This does NOT execute real GenVM Direct Mode, real web networking, network
consensus or real signature authorization. Use direct_tests and StudioNet.
"""
import importlib.util
import sys
import types
import hashlib
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]

class Runtime:
    def __init__(self):
        self.sender = '0xA'
        self.pages = {}
        self.llm = None
        self.validation = None
        self.last_value = None
        self.web_read_count = 0
        self.calls = []

class FakeMap(dict):
    def __class_getitem__(cls, args): return cls
    def get_or_insert_default(self, key):
        if key not in self:
            self[key] = types.SimpleNamespace(representations=[],reliances=[],attempts=[])
        return self[key]

class FakeList(list):
    def __class_getitem__(cls,args): return cls

class FakeContract:
    def __new__(cls,*args,**kwargs):
        obj = super().__new__(cls)
        for name, kind in cls.__annotations__.items():
            if kind is FakeMap:
                setattr(obj,name,FakeMap())
        return obj

class FakeReturn:
    def __init__(self,value): self.calldata=value

class FakeError(Exception): pass

class FakeEvent:
    def __init__(self,*args,**kwargs): pass
    def emit(self): pass

def build_runtime():
    rt=Runtime()
    namespace=types.ModuleType('genlayer')
    class Public:
        @staticmethod
        def write(fn):return fn
        @staticmethod
        def view(fn):return fn
    class VM:
        UserError=FakeError
        Return=FakeReturn
        def run_nondet_unsafe(self,leader,validator):
            value=leader()
            rt.last_value=value
            rt.validation=validator
            return value
    class Web:
        def render(self,url,mode='text'):
            rt.web_read_count+=1
            if url not in rt.pages: raise IOError('unavailable')
            return rt.pages[url]
    class Nondet:
        web=Web()
        def exec_prompt(self,prompt,response_format='json'):
            rt.calls.append(prompt)
            if rt.llm is None: raise IOError('no model')
            return rt.llm(prompt)
    class Message:
        @property
        def sender_address(self): return rt.sender
    namespace.gl=types.SimpleNamespace(Contract=FakeContract, public=Public(), vm=VM(),
        nondet=Nondet(), message=Message(), contract_interface=lambda c:c, Event=FakeEvent)
    namespace.u8=int
    namespace.u32=int
    namespace.u256=int
    namespace.Address=str
    namespace.TreeMap=FakeMap
    namespace.DynArray=FakeList
    namespace.allow_storage=lambda cls: cls
    # Explicit offline hash stub: NOT a GenVM Keccak byte-parity test.
    namespace.Keccak256=lambda bs: hashlib.sha3_256(bs)
    return rt,namespace

@pytest.fixture
def harness(monkeypatch):
    rt,mod=build_runtime()
    monkeypatch.setitem(sys.modules,'genlayer',mod)
    spec=importlib.util.spec_from_file_location('courselock_tested',ROOT/'contracts/courselock.py')
    project=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(project)
    rt.module=project
    rt.contract=project.CourseLock()
    return rt
