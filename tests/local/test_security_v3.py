"""Deterministic randomized state invariants using FAKE SDK, not real consensus."""
import json
import pathlib
import random
import unittest
from sdk_stub import FakeUserError, install_and_load

P=pathlib.Path(__file__).resolve().parents[2]/'contracts/quest_forge.py'
A='0x'+'11'*20
B='0x'+'22'*20
C='0x'+'33'*20
NARRATIVE='Read the public signs and inspect the mechanism carefully.'

class SecurityV3(unittest.TestCase):
    def setUp(self):
        self.sdk,self.mod=install_and_load('quest_v3',str(P))
        self.sdk.message.sender_address=A
        self.clock=[1000]

    def game(self,name='game_01'):
        self.sdk.message.sender_address=A
        c=self.mod.QuestForge()
        c._now=lambda:self.clock[0]
        c.create_game(name,B)
        self.sdk.message.sender_address=B
        c.join_game(name)
        return c

    def state(self,c):
        return json.loads(c.get_game('game_01'))

    def test_seeded_100_game_traces_conserve_resource_bounds(self):
        rng=random.Random(20261122)
        for run in range(100):
            self.clock[0]=1000
            c=self.game()
            for step in range(self.mod.MAX_TURNS):
                s=self.state(c)
                self.assertIn(s['status'],('ACTIVE','WON','LOST'))
                self.assertTrue(0 <= s['stage'] <= 3)
                self.assertTrue(0 <= s['threat'] <= 6)
                self.assertTrue(0 <= s['turn'] <= self.mod.MAX_TURNS)
                for player in (1,2):
                    self.assertTrue(0 <= s[f'energy{player}'] <= 6)
                    self.assertTrue(0 <= s[f'insight{player}'] <= 2)
                if s['status']!='ACTIVE': break
                self.sdk.message.sender_address=s['next']
                key=1 if s['next']==A else 2
                legal=[]
                if s[f'energy{key}']>=2 and s[f'insight{key}']>=1:
                    legal.append('SOLVE')
                if s[f'energy{key}']>=1 and s[f'insight{key}']<2:
                    legal.append('SCOUT')
                if s[f'energy{key}']>=2 and s['threat']>0:
                    legal.append('FORTIFY')
                if s[f'energy{key}']<6:
                    legal.append('REST')
                self.assertTrue(legal, (run,step,s))
                action=rng.choice(legal)
                if action=='SOLVE':
                    label=rng.choice(('PASS','FAIL'))
                    self.sdk.nondet.answers.extend([{'decision':label}]*2)
                c.act('game_01',s['turn'],action,NARRATIVE)
                self.clock[0]+=1
            s=self.state(c)
            self.assertEqual(s['turn'], min(s['turn'],self.mod.MAX_TURNS))
            self.assertTrue(0 <= s['stage'] <= len(self.mod.STAGES))

    def test_disallow_boolean_turn_nonce(self):
        c=self.game()
        self.sdk.message.sender_address=A
        with self.assertRaisesRegex(FakeUserError,'Turn nonce must be integer'):
            c.act('game_01',False,'SCOUT',NARRATIVE)
        self.assertEqual(self.state(c)['turn'],0)

    def test_reject_unicode_display_spoofing(self):
        c=self.game()
        self.sdk.message.sender_address=A
        for ch in ('\u202e','\u2069','\u200b','\ufeff'):
            with self.assertRaises(FakeUserError):
                c.act('game_01',0,'SCOUT',NARRATIVE+ch)
        self.assertEqual(self.state(c)['turn'],0)

    def test_invalid_action_never_changes_turn(self):
        c=self.game()
        self.sdk.message.sender_address=A
        original=self.state(c)
        for action in ('','SUPERWIN','SOLVE\u200e','skip'):
            with self.assertRaises(FakeUserError):
                c.act('game_01',0,action,NARRATIVE)
        self.assertEqual(self.state(c),original)
