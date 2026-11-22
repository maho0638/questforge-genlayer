"""Extra offline invariants with a FAKE SDK; not official Direct Mode."""
import json
import unittest
import pathlib
from sdk_stub import install_and_load, FakeUserError, FakeConsensusError

PATH=pathlib.Path(__file__).resolve().parents[2]/'contracts'/'quest_forge.py'
A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20

def game(c):return json.loads(c.get_game('quest_test'))

class QuestAdversarial(unittest.TestCase):
    def setUp(self):
        self.sdk,self.mod=install_and_load('quest_extras',str(PATH))
        self.sdk.message.sender_address=A
        self.c=self.mod.QuestForge()
        self.t=[1000]
        self.c._now=lambda:self.t[0]
        self.c.create_game('quest_test',B)
        self.sdk.message.sender_address=B
        self.c.join_game('quest_test')
        self.sdk.message.sender_address=A

    def act(self,action,narrative='Inspect this visible puzzle without violating its rules.',verdict='PASS'):
        if action=='SOLVE':self.sdk.nondet.answers.extend([{'decision':verdict}]*2)
        self.c.act('quest_test',game(self.c)['turn'],action,narrative)

    def test_no_turn_loss_on_unknown_llm_label(self):
        before=game(self.c)
        with self.assertRaises(FakeUserError):self.act('SOLVE',verdict='INSTANT_WIN')
        self.assertEqual(game(self.c),before)

    def test_no_turn_loss_on_validator_disagreement(self):
        before=game(self.c)
        self.sdk.nondet.answers.extend([{'decision':'PASS'},{'decision':'FAIL'}])
        with self.assertRaises(FakeConsensusError):self.c.act('quest_test',0,'SOLVE','Cross on the intact bridge without entering river.')
        self.assertEqual(game(self.c),before)

    def test_non_turn_player_cannot_act_even_as_mixed_case(self):
        self.sdk.message.sender_address=B.upper().replace('0X','0x')
        with self.assertRaises(FakeUserError):self.act('SCOUT')
        self.assertEqual(game(self.c)['turn'],0)

    def test_extra_player_cannot_act(self):
        self.sdk.message.sender_address=C
        with self.assertRaises(FakeUserError):self.act('REST')
        self.assertEqual(game(self.c)['turn'],0)

    def test_replay_nonce_rejected_after_alternation(self):
        self.act('SCOUT')
        self.sdk.message.sender_address=B
        with self.assertRaises(FakeUserError):self.c.act('quest_test',0,'SCOUT','Inspect next location and return safely')
        self.assertEqual(game(self.c)['turn'],1)

    def test_fortify_rejects_no_threat_and_no_mutation(self):
        before=game(self.c)
        with self.assertRaises(FakeUserError):self.act('FORTIFY')
        self.assertEqual(game(self.c),before)

    def test_exact_timeout_boundary(self):
        self.t[0]+=self.mod.TURN_EXPIRY-1
        with self.assertRaises(FakeUserError):self.c.claim_timeout('quest_test')
        self.t[0]+=1
        with self.assertRaises(FakeUserError):self.act('SCOUT')
        self.sdk.message.sender_address=B
        self.c.claim_timeout('quest_test')
        self.assertEqual(game(self.c)['winner'],B)
        self.assertEqual(game(self.c)['status'],'FORFEIT')

    def test_loss_is_terminal(self):
        self.act('SOLVE',verdict='FAIL')
        self.sdk.message.sender_address=B
        self.act('SOLVE',verdict='FAIL')
        self.sdk.message.sender_address=A
        self.act('SCOUT')
        self.sdk.message.sender_address=B
        self.act('SCOUT')
        self.assertEqual(game(self.c)['status'],'LOST')
        self.sdk.message.sender_address=A
        with self.assertRaises(FakeUserError):self.act('SCOUT')
        with self.assertRaises(FakeUserError):self.c.claim_timeout('quest_test')

    def test_gaming_ai_never_skips_resource_check(self):
        self.act('SCOUT')
        self.sdk.message.sender_address=B
        self.act('SCOUT')
        self.sdk.message.sender_address=A
        before=game(self.c)
        with self.assertRaises(FakeUserError):self.act('SCOUT')
        self.assertEqual(game(self.c),before)
        self.assertEqual(game(self.c)['insight1'],self.mod.MAX_INSIGHT)
        self.assertGreaterEqual(game(self.c)['energy1'],0)

    def test_new_game_cannot_reuse_id_even_when_terminal(self):
        self.t[0]+=self.mod.TURN_EXPIRY
        self.sdk.message.sender_address=B
        self.c.claim_timeout('quest_test')
        with self.assertRaises(FakeUserError):self.c.create_game('quest_test',A)

if __name__=='__main__':unittest.main()
