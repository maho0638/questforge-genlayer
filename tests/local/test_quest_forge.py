import json
import pathlib
import unittest
from sdk_stub import install_and_load, FakeConsensusError, FakeUserError

PATH = pathlib.Path(__file__).resolve().parents[2] / 'contracts' / 'quest_forge.py'
A = '0x' + '11' * 20
B = '0x' + '22' * 20
C = '0x' + '33' * 20

def body(c, id='quest_01'):
    return json.loads(c.get_game(id))

class QuestForgeTests(unittest.TestCase):
    def setUp(self):
        self.sdk, self.mod = install_and_load('quest_forge_local', str(PATH))
        self.clock = [1000]
        self.sdk.message.sender_address = A
        self.game = self.mod.QuestForge()
        self.game._now = lambda: self.clock[0]

    def create(self):
        self.game.create_game('quest_01', B)

    def join(self):
        self.create()
        self.sdk.message.sender_address = B
        self.game.join_game('quest_01')
        self.sdk.message.sender_address = A

    def act(self, action='SOLVE', narrative='Cross the intact bridge without entering the river.', verdict='PASS'):
        if action == 'SOLVE':
            self.sdk.nondet.answers.extend([{'decision': verdict}, {'decision': verdict}])
        return self.game.act('quest_01', body(self.game)['turn'], action, narrative)

    def test_create_and_join_and_permissions(self):
        self.create()
        self.assertEqual(body(self.game)['status'], 'LOBBY')
        with self.assertRaises(FakeUserError): self.game.join_game('quest_01')
        self.sdk.message.sender_address = C
        with self.assertRaises(FakeUserError): self.game.join_game('quest_01')
        self.sdk.message.sender_address = B
        self.game.join_game('quest_01')
        self.assertEqual(body(self.game)['status'], 'ACTIVE')

    def test_creator_must_not_invite_self(self):
        with self.assertRaises(FakeUserError): self.game.create_game('quest_01', A)

    def test_duplicate_game_id_blocked(self):
        self.create()
        with self.assertRaises(FakeUserError): self.game.create_game('quest_01', B)

    def test_full_cooperative_win_and_turn_receipts(self):
        self.join()
        self.act('SOLVE', 'I cross the intact stone bridge and stay clear of the water.')
        self.sdk.message.sender_address = B
        self.act('SOLVE', 'Pull the DAWN lever first, then pull ECHO without forcing the gate.')
        self.sdk.message.sender_address = A
        self.act('SCOUT', 'Examine the beacon instructions on the wall for clues.')
        self.sdk.message.sender_address = B
        self.act('SCOUT', 'Study the controls to understand their required order.')
        self.sdk.message.sender_address = A
        self.act('SOLVE', 'Activate GREEN first, BLUE next, and do not damage the beacon.')
        g = body(self.game)
        self.assertEqual(g['status'], 'WON')
        self.assertEqual(g['winner'], 'COOPERATIVE')
        self.assertEqual(g['stage'], 3)
        self.assertEqual(g['turn'], 5)
        receipt = json.loads(self.game.get_turn('quest_01', 4))
        self.assertEqual(receipt['decision'], 'PASS')
        self.assertEqual(receipt['stage_before'], 2)
        self.assertEqual(receipt['stage_after'], 3)

    def test_wrong_actor_and_replay_nonce_rejected(self):
        self.join()
        self.sdk.message.sender_address = B
        with self.assertRaises(FakeUserError):
            self.game.act('quest_01', 0, 'SCOUT', 'Look carefully at the river crossing.')
        self.sdk.message.sender_address = A
        self.act('SCOUT', 'Look carefully at the river crossing.')
        self.sdk.message.sender_address = B
        with self.assertRaises(FakeUserError):
            self.game.act('quest_01', 0, 'SCOUT', 'Look carefully at the gate inscription.')
        self.assertEqual(body(self.game)['turn'], 1)

    def test_validation_disagreement_no_state_mutation(self):
        self.join()
        self.sdk.nondet.answers.extend([{'decision': 'PASS'}, {'decision': 'FAIL'}])
        before = body(self.game)
        with self.assertRaises(FakeConsensusError):
            self.game.act('quest_01', 0, 'SOLVE', 'Cross over the intact stone bridge.')
        self.assertEqual(body(self.game), before)
        self.assertEqual(self.game.get_turn('quest_01', 0), '')

    def test_undetermined_never_drains_resources(self):
        self.join()
        before = body(self.game)
        self.sdk.nondet.answers.extend([{'decision': 'UNDETERMINED'}] * 2)
        with self.assertRaises(FakeUserError):
            self.game.act('quest_01', 0, 'SOLVE', 'Maybe try to cross using unknown magic.')
        self.assertEqual(body(self.game), before)

    def test_failed_attempt_increases_threat_not_progress(self):
        self.join()
        self.act('SOLVE', 'Jump straight into the turbulent river and swim.', 'FAIL')
        self.assertEqual(body(self.game)['stage'], 0)
        self.assertEqual(body(self.game)['threat'], 2)

    def test_fortify_and_rest_actions_conserve_bounds(self):
        self.join()
        with self.assertRaises(FakeUserError):
            self.act('REST', 'Rest for recovery before starting the mission.')
        self.act('SCOUT', 'Scout the landscape and inspect the bridge carefully.')
        self.sdk.message.sender_address = B
        self.act('SCOUT', 'Scout the stone inscriptions and path to the gate.')
        self.sdk.message.sender_address = A
        self.act('FORTIFY', 'Fortify the camp from rising danger in the region.')
        self.assertEqual(body(self.game)['threat'], 1)
        self.sdk.message.sender_address = B
        self.act('REST', 'Rest at the safe campsite and restore your energy.')
        self.assertEqual(body(self.game)['energy2'], 6)
        self.assertEqual(body(self.game)['threat'], 2)

    def test_invitation_expiration_and_public_cancellation(self):
        self.create()
        self.clock[0] += self.mod.LOBBY_EXPIRY
        self.sdk.message.sender_address = B
        with self.assertRaises(FakeUserError): self.game.join_game('quest_01')
        self.sdk.message.sender_address = C
        self.game.cancel_lobby('quest_01')
        self.assertEqual(body(self.game)['status'], 'CANCELLED')

    def test_non_creator_cannot_cancel_open_lobby(self):
        self.create()
        self.sdk.message.sender_address = B
        with self.assertRaises(FakeUserError): self.game.cancel_lobby('quest_01')

    def test_stall_timeout_forfeit_restricted_to_opponent(self):
        self.join()
        self.clock[0] += self.mod.TURN_EXPIRY
        with self.assertRaises(FakeUserError):
            self.game.claim_timeout('quest_01')
        self.sdk.message.sender_address = B
        self.game.claim_timeout('quest_01')
        self.assertEqual(body(self.game)['winner'], B)
        self.assertEqual(body(self.game)['status'], 'FORFEIT')

    def test_wrong_player_not_allowed_to_claim_timeout(self):
        self.join()
        self.clock[0] += self.mod.TURN_EXPIRY
        self.sdk.message.sender_address = C
        with self.assertRaises(FakeUserError): self.game.claim_timeout('quest_01')

    def test_narrative_digest_not_raw_text_onchain_receipt(self):
        self.join()
        narrative = 'Scout the intact river crossing from a safe rock.'
        self.act('SCOUT', narrative)
        receipt = self.game.get_turn('quest_01', 0)
        self.assertNotIn(narrative, receipt)
        self.assertEqual(json.loads(receipt)['narrative_sha256'], self.mod._hash(narrative))

    def test_invalid_action_rejected(self):
        self.join()
        with self.assertRaises(FakeUserError): self.act('WIN', 'I win this whole game immediately!')
        self.assertEqual(body(self.game)['turn'], 0)

    def test_stage_cannot_be_read_out_of_range(self):
        with self.assertRaises(FakeUserError): self.game.get_stage(3)
        self.assertIn('bridge', self.game.get_stage(0))


    def test_threat_meter_is_hard_capped_at_six(self):
        self.join()
        self.act('SOLVE', 'Jump directly into the rapid water to cross.', 'FAIL')
        self.sdk.message.sender_address = B
        self.act('SOLVE', 'Try to swim downstream against the rocks.', 'FAIL')
        self.sdk.message.sender_address = A
        self.act('SCOUT', 'Scout the stone bridge for alternate routes.')
        self.sdk.message.sender_address = B
        self.act('SCOUT', 'Scout the nearby river banks and shore.')
        g = body(self.game)
        self.assertEqual(g['threat'], 6)
        self.assertEqual(g['status'], 'LOST')

    def test_game_turn_expiry_prevents_accepted_new_move(self):
        self.join()
        self.clock[0] += self.mod.TURN_EXPIRY
        with self.assertRaises(FakeUserError):
            self.game.act('quest_01', 0, 'SCOUT', 'Scout around the crossing for clues.')
        self.assertEqual(body(self.game)['turn'], 0)

    def test_only_creator_can_cancel_lobby_before_deadline(self):
        self.create()
        self.game.cancel_lobby('quest_01')
        self.assertEqual(body(self.game)['status'], 'CANCELLED')
        self.sdk.message.sender_address = B
        with self.assertRaises(FakeUserError): self.game.join_game('quest_01')

    def test_invalid_llm_label_does_not_consume_turn(self):
        self.join()
        self.sdk.nondet.answers.extend([{'decision':'WIN'}] * 2)
        with self.assertRaises(FakeUserError):
            self.game.act('quest_01', 0, 'SOLVE', 'Cross the bridge using approved steps.')
        self.assertEqual(body(self.game)['turn'], 0)
        self.assertEqual(body(self.game)['energy1'], 6)

if __name__ == '__main__':
    unittest.main()
