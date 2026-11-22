"""OFFICIAL GenLayer direct-mode suite; requires genlayer-test, not the local fake."""
import json


def addr(wallet):
    return '0x' + wallet.hex()


def test_quest_forge_real_direct_play(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('quest_01', addr(direct_bob))
    assert json.loads(c.get_game('quest_01'))['status'] == 'LOBBY'
    direct_vm.sender = direct_bob
    c.join_game('quest_01')
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r'(?s).*two-player cooperative puzzle.*', json.dumps({'decision':'PASS'}))
    c.act('quest_01', 0, 'SOLVE', 'I cross on the intact stone bridge and never enter the water.')
    game = json.loads(c.get_game('quest_01'))
    assert game['stage'] == 1 and game['turn'] == 1
    assert direct_vm.run_validator() is True
    with direct_vm.expect_revert('Not your turn'):
        c.act('quest_01', 1, 'SCOUT', 'Inspect the next obstacle carefully.')


def test_quest_forge_validator_disagreement(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('quest_02', addr(direct_bob))
    direct_vm.sender = direct_bob
    c.join_game('quest_02')
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r'(?s).*two-player cooperative puzzle.*', json.dumps({'decision':'PASS'}))
    c.act('quest_02', 0, 'SOLVE', 'Walk over the intact bridge without stepping into the river.')
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r'(?s).*two-player cooperative puzzle.*', json.dumps({'decision':'FAIL'}))
    assert direct_vm.run_validator() is False


def test_quest_forge_real_direct_full_win(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('quest_03', addr(direct_bob))
    direct_vm.sender = direct_bob
    c.join_game('quest_03')
    direct_vm.mock_llm(r'(?s).*two-player cooperative puzzle.*', json.dumps({'decision':'PASS'}))
    direct_vm.sender = direct_alice
    c.act('quest_03', 0, 'SOLVE', 'Cross the intact stone bridge without entering the river.')
    direct_vm.sender = direct_bob
    c.act('quest_03', 1, 'SOLVE', 'Activate DAWN lever first, followed by ECHO lever, without force.')
    direct_vm.sender = direct_alice
    c.act('quest_03', 2, 'SCOUT', 'Inspect the beacon operating rules for next action.')
    direct_vm.sender = direct_bob
    c.act('quest_03', 3, 'SCOUT', 'Inspect the beacon controls and the color markings.')
    direct_vm.sender = direct_alice
    c.act('quest_03', 4, 'SOLVE', 'Activate GREEN first, then BLUE, while preserving the beacon.')
    state = json.loads(c.get_game('quest_03'))
    assert state['status'] == 'WON' and state['turn'] == 5 and state['stage'] == 3
    with direct_vm.expect_revert('Game not active'):
        c.act('quest_03', 5, 'SCOUT', 'This extra move must fail after winning.')


def test_quest_forge_real_direct_timeout(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.warp('2026-11-01T00:00:00Z')
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('quest_04', addr(direct_bob))
    direct_vm.sender = direct_bob
    c.join_game('quest_04')
    direct_vm.warp('2026-11-03T00:00:00Z')
    with direct_vm.expect_revert('Stalling player cannot claim win'):
        direct_vm.sender = direct_alice
        c.claim_timeout('quest_04')
    direct_vm.sender = direct_bob
    c.claim_timeout('quest_04')
    state = json.loads(c.get_game('quest_04'))
    assert state['status'] == 'FORFEIT' and state['winner'] == addr(direct_bob).lower()


def test_quest_forge_real_direct_bad_nonce(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('quest_05', addr(direct_bob))
    direct_vm.sender = direct_bob
    c.join_game('quest_05')
    direct_vm.sender = direct_alice
    c.act('quest_05', 0, 'SCOUT', 'Read the signs and observe the stone bridge carefully.')
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert('Stale turn nonce'):
        c.act('quest_05', 0, 'SCOUT', 'Read the signs and observe the stone bridge carefully.')
    assert json.loads(c.get_game('quest_05'))['turn'] == 1


def test_quest_active_capacity_reusable_after_cancel(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('life_one', addr(direct_bob))
    c.create_game('life_two', addr(direct_bob))
    assert int(c.get_active_game_count()) == 2
    with direct_vm.expect_revert('Creator active game capacity exhausted'):
        c.create_game('life_three', addr(direct_bob))
    c.cancel_lobby('life_one')
    c.create_game('life_three', addr(direct_bob))
    assert int(c.get_active_game_count()) == 2
    assert int(c.get_game_count()) == 3
    with direct_vm.expect_revert('Duplicate game ID'):
        c.create_game('life_one', addr(direct_bob))


def test_quest_expired_active_game_cleanup(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    direct_vm.warp('2026-11-01T00:00:00Z')
    direct_vm.sender = direct_alice
    c = direct_deploy('contracts/quest_forge.py')
    c.create_game('abandoned', addr(direct_bob))
    direct_vm.sender = direct_bob
    c.join_game('abandoned')
    direct_vm.sender = direct_charlie
    direct_vm.warp('2026-11-07T23:59:59Z')
    with direct_vm.expect_revert('Neutral expiry not reached'):
        c.expire_stalled_game('abandoned')
    direct_vm.warp('2026-11-08T00:00:00Z')
    c.expire_stalled_game('abandoned')
    assert int(c.get_active_game_count()) == 0
    state = json.loads(c.get_game('abandoned'))
    assert state['status'] == 'EXPIRED' and state['winner'] == 'NONE'
    with direct_vm.expect_revert('Game not active'):
        c.expire_stalled_game('abandoned')
