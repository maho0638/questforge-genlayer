"""Pure Python deterministic fake for LOCAL LOGIC tests, NOT real GenVM."""
import sys
import types
import importlib.util

class FakeUserError(Exception):
    pass

class FakeConsensusError(Exception):
    pass

class TreeMap(dict):
    @classmethod
    def __class_getitem__(cls, _type):
        return cls

class DynArray(list):
    @classmethod
    def __class_getitem__(cls, _type):
        return cls

class Return:
    def __init__(self, calldata):
        self.calldata = calldata

class Public:
    def __init__(self):
        self.write = lambda fn: fn
        self.view = lambda fn: fn

class VM:
    UserError = FakeUserError
    Return = Return
    def __init__(self, sdk):
        self.sdk = sdk
    def run_nondet_unsafe(self, leader_fn, validator_fn):
        value = leader_fn()
        if not validator_fn(Return(value)):
            raise FakeConsensusError("Leader and validator disagree")
        return value

class Nondet:
    def __init__(self):
        self.answers = []
    def exec_prompt(self, _prompt, response_format=None):
        if not self.answers:
            raise AssertionError("Missing local fake-LLM response")
        return self.answers.pop(0)

class SDK:
    Contract = object
    def __init__(self):
        self.message = types.SimpleNamespace(sender_address="")
        self.public = Public()
        self.nondet = Nondet()
        self.vm = VM(self)


def install_and_load(module_name: str, file_path: str):
    sdk = SDK()
    module = types.ModuleType("genlayer")
    module.gl = sdk
    module.TreeMap = TreeMap
    module.DynArray = DynArray
    module.Address = lambda x: str(x).lower()
    module.u32 = int
    module.__all__ = ["gl", "TreeMap", "DynArray", "Address", "u32"]
    sys.modules["genlayer"] = module
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    contract_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contract_module)
    return sdk, contract_module
