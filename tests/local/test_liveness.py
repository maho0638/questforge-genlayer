"""Active-slot recovery and neutral stalled-session cleanup; fake SDK only."""
import json
from pathlib import Path
import pytest
from sdk_stub import install_and_load,FakeUserError

A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20

@pytest.fixture
def ctx():
    sdk,mod=install_and_load('quest_liveness',str(Path(__file__).resolve().parents[2]/'contracts/quest_forge.py'))
    sdk.message.sender_address=A
    c=mod.QuestForge()
    now=[10_000]
    c._now=lambda:now[0]
    return sdk,mod,c,now

def game(c,id):
    return json.loads(c.get_game(id))

def test_creator_slots_released_on_cancel_and_ids_preserved(ctx):
    sdk,mod,c,t=ctx
    c.create_game('game_one',B)
    c.create_game('game_two',B)
    assert c.get_active_game_count()==2
    with pytest.raises(FakeUserError,match='Creator active game'):
        c.create_game('game_three',B)
    c.cancel_lobby('game_one')
    assert c.get_active_game_count()==1
    c.create_game('game_three',B)
    assert c.get_game_count()==3
    assert game(c,'game_one')['status']=='CANCELLED'
    with pytest.raises(FakeUserError,match='Duplicate game ID'):
        c.create_game('game_one',B)

def test_forfeit_releases_slot_exactly_once(ctx):
    sdk,mod,c,t=ctx
    c.create_game('game_one',B)
    sdk.message.sender_address=B
    c.join_game('game_one')
    t[0]+=mod.TURN_EXPIRY
    c.claim_timeout('game_one')
    assert c.get_active_game_count()==0
    assert int(c.get_creator_active_count(A))==0
    with pytest.raises(FakeUserError,match='No timeout claim'):
        c.claim_timeout('game_one')
    sdk.message.sender_address=A
    c.create_game('game_two',B)
    assert c.get_active_game_count()==1

def test_stale_cleanup_only_after_grace_and_prevents_double_release(ctx):
    sdk,mod,c,t=ctx
    c.create_game('game_one',B)
    sdk.message.sender_address=B
    c.join_game('game_one')
    sdk.message.sender_address=C
    t[0]+=mod.STALE_GAME_EXPIRY-1
    with pytest.raises(FakeUserError,match='not reached'):
        c.expire_stalled_game('game_one')
    t[0]+=1
    c.expire_stalled_game('game_one')
    assert game(c,'game_one')['status']=='EXPIRED'
    assert game(c,'game_one')['winner']=='NONE'
    assert c.get_active_game_count()==0
    with pytest.raises(FakeUserError,match='Game not active'):
        c.expire_stalled_game('game_one')

def test_terminal_win_frees_capacity(ctx):
    sdk,mod,c,t=ctx
    c.create_game('game_one',B)
    sdk.message.sender_address=B
    c.join_game('game_one')
    sdk.nondet.answers=[{'decision':'PASS'}]*6
    sdk.message.sender_address=A
    c.act('game_one',0,'SOLVE','Cross on intact stone bridge without touching the water.')
    sdk.message.sender_address=B
    c.act('game_one',1,'SOLVE','Activate DAWN then ECHO exactly in this order without force.')
    sdk.message.sender_address=A
    c.act('game_one',2,'SCOUT','Inspect the colors and rules on the beacon.')
    sdk.message.sender_address=B
    c.act('game_one',3,'SCOUT','Study the beacon instructions and colored controls.')
    sdk.message.sender_address=A
    c.act('game_one',4,'SOLVE','Activate GREEN before BLUE and keep the beacon intact.')
    assert game(c,'game_one')['status']=='WON'
    assert c.get_active_game_count()==0
    with pytest.raises(FakeUserError,match='Game not active'):
        c.expire_stalled_game('game_one')

def test_more_than_128_simultaneous_games_cannot_globally_block_new_users(ctx):
    sdk,mod,c,t=ctx
    # Many different creators cannot exhaust an artificial global slot ceiling.
    for j in range(129):
        sdk.message.sender_address='0x'+f'{j+1:040x}'
        c.create_game(f'game_{j:05d}', B if sdk.message.sender_address!=B else A)
    assert c.get_active_game_count()==129
    sdk.message.sender_address='0x'+f'{1:040x}'
    c.cancel_lobby('game_00000')
    assert c.get_active_game_count()==128
    sdk.message.sender_address='0x'+f'{130:040x}'
    c.create_game('game_00129', B)
    assert c.get_active_game_count()==129
    assert c.get_game_count()==130
