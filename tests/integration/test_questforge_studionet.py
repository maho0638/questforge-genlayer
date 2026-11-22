"""Unmocked hosted Studionet proof: consensus-refereed game and persistent turns."""
import json
import hashlib
import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

def tx_hash(value):
    if isinstance(value, dict):
        return str(value.get("hash") or value.get("transaction_hash") or "")
    return str(getattr(value, "hash", ""))


def write(method, *args, consensus=False):
    opts = {"wait_interval": 10000, "wait_retries": 100}
    if consensus:
        opts["consensus_max_rotations"] = 4
    result = method(args=list(args)).transact(**opts)
    assert tx_execution_succeeded(result)
    return result


@pytest.mark.integration
def test_questforge_live_consensus_game(default_account, accounts):
    assert len(accounts) >= 2, "Live Studio must provide two accounts"
    first_address = str(default_account.address)
    second_address = str(accounts[1].address)
    assert first_address.lower() != second_address.lower()

    factory = get_contract_factory("QuestForge")
    contract = factory.deploy(account=default_account, consensus_max_rotations=4)
    print("QUESTFORGE_CONTRACT=" + str(contract.address), flush=True)
    first = contract.connect(account=default_account)
    second = contract.connect(account=accounts[1])

    created = write(first.create_game, "live_bridge_v1", second_address)
    print("QUESTFORGE_CREATE_TX=" + tx_hash(created), flush=True)
    joined = write(second.join_game, "live_bridge_v1")
    print("QUESTFORGE_JOIN_TX=" + tx_hash(joined), flush=True)
    game = json.loads(contract.get_game(args=["live_bridge_v1"]).call())
    assert game["status"] == "ACTIVE" and int(game["turn"]) == 0
    assert game["next"].lower() == first_address.lower()

    bridge_move = (
        "I cross the cold river only by walking over the existing intact stone "
        "bridge. I stay out of the water, do not use a boat and do not damage "
        "or destroy the bridge."
    )
    solve = write(first.act, "live_bridge_v1", 0, "SOLVE", bridge_move, consensus=True)
    print("QUESTFORGE_SOLVE_TX=" + tx_hash(solve), flush=True)
    current = json.loads(contract.get_game(args=["live_bridge_v1"]).call())
    trace = json.loads(contract.get_turn(args=["live_bridge_v1", 0]).call())
    print("QUESTFORGE_DECISION=" + str(trace["decision"]), flush=True)
    print("QUESTFORGE_STATUS=" + str(current["status"]), flush=True)
    assert trace["actor"].lower() == first_address.lower()
    assert trace["action"] == "SOLVE"
    assert trace["decision"] in ("PASS", "FAIL")
    assert trace["narrative_sha256"] == hashlib.sha256(bridge_move.encode()).hexdigest()
    assert current["status"] == "ACTIVE" and int(current["turn"]) == 1
    assert int(current["stage"]) == (1 if trace["decision"] == "PASS" else 0)
    assert current["next"].lower() == second_address.lower()

    scout = write(second.act, "live_bridge_v1", 1, "SCOUT",
                  "I carefully inspect the next obstacle and examine the route.")
    print("QUESTFORGE_SCOUT_TX=" + tx_hash(scout), flush=True)
    after = json.loads(contract.get_game(args=["live_bridge_v1"]).call())
    assert int(after["turn"]) == 2
    assert after["status"] == "ACTIVE"
    assert after["next"].lower() == first_address.lower()
    print("QUESTFORGE_LIVE_PROOF=FINALIZED_READ_ASSERTIONS_PASS", flush=True)
