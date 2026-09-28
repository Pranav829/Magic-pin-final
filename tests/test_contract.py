"""Offline contract checks; no API key or external requests required."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bot import main as server
from fastapi.testclient import TestClient
from bot.context_store import ContextStore
from bot.conversation_tracker import ConversationTracker


class ContractTests(unittest.TestCase):
    def setUp(self):
        server.store = ContextStore()
        server.tracker = ConversationTracker()
        server._sent_suppression_keys.clear()
        self.client = TestClient(server.app)

    def push(self, version=1, payload=None, scope='merchant'):
        return self.client.post('/v1/context', json={
            'scope': scope, 'context_id': 'test', 'version': version,
            'payload': payload or {'name': 'original'},
            'delivered_at': '2026-09-27T00:00:00Z',
        })

    def test_identity(self):
        data = self.client.get('/v1/metadata').json()
        self.assertEqual(data['team_name'], 'Pranav Verma')
        self.assertEqual(data['team_members'], ['Pranav Verma'])
        self.assertEqual(data['contact_email'], 'pranavv829@gmail.com')

    def test_duplicate_is_successful_noop(self):
        first = self.push()
        again = self.push(payload={'name': 'must not replace'})
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.json()['accepted'])
        self.assertEqual(first.json()['ack_id'], again.json()['ack_id'])
        self.assertEqual(server.store.get_merchant('test')['name'], 'original')

    def test_stale_version_conflict(self):
        self.push(version=2)
        response = self.push(version=1)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['current_version'], 2)

    def test_newer_version_replaces(self):
        self.push()
        self.push(version=2, payload={'name': 'updated'})
        self.assertEqual(server.store.get_merchant('test')['name'], 'updated')

    def test_invalid_scope(self):
        self.assertEqual(self.push(scope='invalid').status_code, 400)
        self.assertEqual(sum(server.store.counts().values()), 0)

    def test_empty_tick_and_health(self):
        response = self.client.post('/v1/tick', json={'now': '2026-09-27T00:00:00Z'})
        self.assertEqual(response.json(), {'actions': []})
        self.assertEqual(self.client.get('/v1/healthz').json()['status'], 'ok')

    def test_hostile_reply_suppresses_merchant_without_llm(self):
        with patch.object(server, 'compose_reply', side_effect=AssertionError('Unexpected LLM call')):
            response = self.client.post('/v1/reply', json={
                'conversation_id': 'test', 'merchant_id': 'test',
                'from_role': 'merchant', 'message': 'Stop messaging me. This is useless spam.',
                'received_at': '2026-09-27T00:00:00Z', 'turn_number': 2,
            })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(server.tracker.is_merchant_suppressed('test'))


if __name__ == '__main__':
    unittest.main()
