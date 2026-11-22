"""Live Studionet full-win lifecycle. Real LLM, real validator consensus; no mocked responses."""
import json
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

GAME_ID = "full_win_proof_20261122"
MOVES = (
    ("SOLVE", "I walk across the existing intact stone bridge to reach the other bank. I never enter the cold river, use a boat, or damage the bridge.", 1),
    ("SOLVE", "I first operate the lever clearly labelled DAWN. Only after completing the DAWN action, I operate the lever clearly labelled ECHO second. I do not use force to bypass the stone gate.", 2),
    ("SCOUT", "I examine the controls and carefully inspect the posted operating instructions.", 2),
    ("SCOUT", "I carefully inspect the beacon and read the color-coded operating rules again.", 2),
    ("SOLVE", "I activate the GREEN beacon control first. Only after GREEN activation do I activate the BLUE control second. I leave the beacon fully intact and undamaged.", 3),
)

def tx_hash(receipt):
    return str(receipt.get("hash") or receipt.get("transaction_hash") or "") if isinstance(receipt, dict) else str(getattr(receipt, "hash", ""))

def submit(contract, action, args, semantic=False):
    settings={"wait_interval":10000,"wait_retries":100}
    if semantic:
        settings["consensus_max_rotations"]=4
    receipt=getattr(contract,action)(args=args).transact(**settings)
    assert tx_execution_succeeded(receipt), f"{action} did not execute successfully"
    h=tx_hash(receipt)
    assert h.startswith("0x") and len(h)==66, f"Missing valid {action} tx hash"
    print("FULLWIN_TX_"+action.upper()+"="+h,flush=True)
    return h

@pytest.mark.integration
def test_questforge_live_full_cooperative_victory(default_account,accounts):
    assert len(accounts)>=2, "Two real signing accounts required"
    a,b=default_account,accounts[1]
    assert str(a.address).lower()!=str(b.address).lower()
    factory=get_contract_factory("QuestForge")
    contract=factory.deploy(account=a,consensus_max_rotations=4)
    print("FULLWIN_CONTRACT="+str(contract.address),flush=True)
    p1,p2=contract.connect(account=a),contract.connect(account=b)
    submit(p1,"create_game",[GAME_ID,str(b.address)])
    submit(p2,"join_game",[GAME_ID])
    for nonce,(action,move,expected_stage) in enumerate(MOVES):
        actor=p1 if nonce%2==0 else p2
        submit(actor,"act",[GAME_ID,nonce,action,move],semantic=(action=="SOLVE"))
        state=json.loads(contract.get_game(args=[GAME_ID]).call())
        receipt=json.loads(contract.get_turn(args=[GAME_ID,nonce]).call())
        assert receipt["action"]==action
        assert int(state["turn"])==nonce+1
        print("FULLWIN_TURN="+str(nonce)+" ACTION="+action+" DECISION="+str(receipt["decision"])+" STAGE="+str(state["stage"])+" THREAT="+str(state["threat"])+" STATUS="+str(state["status"]),flush=True)
        if action=="SOLVE":
            assert receipt["decision"]=="PASS", f"Real AI did not approve stage {nonce}"
        assert int(state["stage"])==expected_stage, "Unexpected stage progression"
        assert str(state["status"])==("WON" if nonce==4 else "ACTIVE")
    assert state["winner"]=="COOPERATIVE"
    assert int(state["stage"])==3
    assert int(state["turn"])==5
    assert int(contract.get_active_game_count().call())==0
    assert int(contract.get_creator_active_count(args=[str(a.address)]).call())==0
    print("FULLWIN_FINAL_STATUS=WON",flush=True)
    print("FULLWIN_PROOF=ALL_5_TURNS_REAL_CONSENSUS_AND_FINAL_READBACKS_PASS",flush=True)
