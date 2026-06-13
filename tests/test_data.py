#!/usr/bin/env python3
"""Tests for data loading, content validation, and data models."""

import json
import os
import sys
import unittest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.models import (
    Server, Mission, Email, Exploit,
    HardwareItem, GovernmentIntel,
)
from engine.validation import ContentValidator


class TestModels(unittest.TestCase):
    """Dataclass model creation and conversion."""

    def test_server_from_dict(self):
        d = {
            'name': '192.168.1.1',
            'ports': [22, 80, 443],
            'key_bits': 2048,
            'files': [{'name': 'readme.txt', 'content': 'hello'}],
            'money': 500,
            'desc': 'A test server',
            'links_raw': ['10.0.0.1'],
            'cracked': {22: True},
            'decrypted': False,
            'scanned': True,
            'is_gov': False,
            'pos': [10.0, 20.0],
        }
        server = Server.from_dict(d)
        self.assertEqual(server.name, '192.168.1.1')
        self.assertEqual(len(server.files), 1)
        self.assertEqual(server.files[0].name, 'readme.txt')
        self.assertEqual(server.money, 500)
        self.assertEqual(server.pos, (10.0, 20.0))

    def test_server_to_dict(self):
        server = Server(
            name='target.test',
            ports=[80],
            key_bits=1024,
            files=[],
            money=0,
            desc='test',
        )
        d = server.to_dict()
        self.assertEqual(d['name'], 'target.test')
        self.assertIn('files', d)

    def test_mission_from_dict(self):
        d = {
            'id': 'test_01',
            'name': 'Test Mission',
            'lvl': 2,
            'desc': 'A test',
            'obj_type': 'download',
            'target': '10.0.0.1',
            'obj_file': 'data.txt',
            'reward': 500,
        }
        m = Mission.from_dict(d)
        self.assertEqual(m.id, 'test_01')
        self.assertEqual(m.obj_type, 'download')
        self.assertEqual(m.reward, 500)

    def test_mission_defaults(self):
        m = Mission.from_dict({})
        self.assertEqual(m.id, '')
        self.assertEqual(m.lvl, 1)
        self.assertEqual(m.done, False)

    def test_exploit_from_dict(self):
        d = {
            'id': 'nmap',
            'name': 'Nmap',
            'desc': 'Port scanner',
            'cost': 100,
            'level': 1,
            'type': 'tool',
            'effect': 'scan',
        }
        ex = Exploit.from_dict(d)
        self.assertEqual(ex.id, 'nmap')
        self.assertEqual(ex.cost, 100)

    def test_email_from_dict(self):
        d = {'id': 'e1', 'lvl': 1, 'sub': 'Hello', 'body': 'Test'}
        e = Email.from_dict(d)
        self.assertEqual(e.sub, 'Hello')
        self.assertEqual(e.body, 'Test')

    def test_hardware_from_list(self):
        h = HardwareItem.from_list(['CPU', 'cpu', 'Processor', 1000, 1.5, 5])
        self.assertEqual(h.name, 'CPU')
        self.assertEqual(h.key, 'cpu')
        self.assertEqual(h.base_cost, 1000)
        self.assertEqual(h.max_level, 5)
        self.assertEqual(h.to_list(), ['CPU', 'cpu', 'Processor', 1000, 1.5, 5])

    def test_intel_from_list(self):
        g = GovernmentIntel.from_list(['g00', 'Passwords', 500, 3])
        self.assertEqual(g.id, 'g00')
        self.assertEqual(g.value, 500)

    def test_server_bounce_defaults(self):
        server = Server(name='b', ports=[1], key_bits=128, files=[], money=0, desc='')
        self.assertEqual(server.bounce_used, 0)
        self.assertEqual(server.visited, False)

    def test_server_visible_flag(self):
        server = Server.from_dict({
            'name': 'visible', 'ports': [80], 'key_bits': 128,
            'files': [], 'money': 0, 'desc': '', 'visible': True,
            'entry_point': True,
        })
        self.assertTrue(server.visible)
        self.assertTrue(server.entry_point)


class TestValidation(unittest.TestCase):
    """ContentValidator edge cases."""

    def setUp(self):
        self.v = ContentValidator(silent=True)

    def test_server_valid(self):
        pool = [['srv1', [22, 80], 256, [], 100, 'desc']]
        result = self.v.validate_server_pool(pool)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(self.v.errors), 0)

    def test_server_invalid_type(self):
        pool = ['not_a_list']
        result = self.v.validate_server_pool(pool)
        self.assertEqual(len(result), 0)
        self.assertGreater(len(self.v.errors), 0)

    def test_server_short_entry(self):
        pool = [['too_short']]
        result = self.v.validate_server_pool(pool)
        self.assertEqual(len(result), 0)

    def test_server_bad_ports(self):
        pool = [['srv', 'not_ports', 128, [], 0, 'desc']]
        self.v.validate_server_pool(pool)
        self.assertGreater(len(self.v.errors), 0)

    def test_server_weak_key_warning(self):
        pool = [['srv', [80], 64, [], 0, 'desc']]
        self.v.validate_server_pool(pool)
        # weak key should be a warning, not error
        self.assertGreater(len(self.v.warnings), 0)

    def test_server_bad_files(self):
        pool = [['srv', [80], 128, [{'bad': 'format'}], 0, 'desc']]
        self.v.validate_server_pool(pool)
        self.assertGreater(len(self.v.errors), 0)

    def test_server_non_numeric_money(self):
        pool = [['srv', [80], 128, [], 'free', 'desc']]
        self.v.validate_server_pool(pool)
        self.assertGreater(len(self.v.warnings), 0)

    def test_hardware_valid(self):
        hw = [['CPU', 'cpu', 'Central Processor', 1000, 1.5, 5]]
        result = self.v.validate_hardware(hw)
        self.assertEqual(len(result), 1)

    def test_hardware_bad_cost(self):
        hw = [['Bad', 'b', 'x', -100, 1.0, 3]]
        result = self.v.validate_hardware(hw)
        self.assertEqual(len(result), 0)

    def test_hardware_bad_max_level(self):
        hw = [['Bad', 'b', 'x', 100, 1.0, 0]]
        result = self.v.validate_hardware(hw)
        self.assertEqual(len(result), 0)

    def test_exploit_valid(self):
        exs = [{'id': 'e1', 'name': 'Tool', 'desc': 'x', 'cost': 100}]
        result = self.v.validate_exploits(exs)
        self.assertEqual(len(result), 1)

    def test_exploit_missing_id(self):
        exs = [{'name': 'NoID', 'desc': 'x', 'cost': 0}]
        result = self.v.validate_exploits(exs)
        self.assertEqual(len(result), 0)

    def test_exploit_duplicate_id(self):
        exs = [
            {'id': 'dup', 'name': 'A', 'desc': 'x', 'cost': 0},
            {'id': 'dup', 'name': 'B', 'desc': 'x', 'cost': 0},
        ]
        result = self.v.validate_exploits(exs)
        self.assertEqual(len(result), 1)  # only first kept

    def test_exploit_negative_cost(self):
        exs = [{'id': 'e1', 'name': 'Bad', 'desc': 'x', 'cost': -50}]
        result = self.v.validate_exploits(exs)
        self.assertEqual(len(result), 0)

    def test_story_missions_valid(self):
        ms = [{'id': 'm1', 'name': 'M', 'lvl': 1, 'desc': 'x', 'obj_type': 'download'}]
        result = self.v.validate_story_missions(ms)
        self.assertEqual(len(result), 1)

    def test_story_missions_missing_id(self):
        ms = [{'name': 'NoID', 'lvl': 1, 'desc': 'x', 'obj_type': 'download'}]
        result = self.v.validate_story_missions(ms)
        self.assertEqual(len(result), 0)

    def test_story_missions_duplicate_id(self):
        ms = [
            {'id': 'm1', 'name': 'A', 'lvl': 1, 'desc': 'x', 'obj_type': 'download'},
            {'id': 'm1', 'name': 'B', 'lvl': 1, 'desc': 'x', 'obj_type': 'download'},
        ]
        result = self.v.validate_story_missions(ms)
        self.assertEqual(len(result), 1)

    def test_story_missions_unknown_obj_type(self):
        ms = [{'id': 'm1', 'name': 'M', 'lvl': 1, 'desc': 'x', 'obj_type': 'unknown_type'}]
        self.v.validate_story_missions(ms)
        self.assertGreater(len(self.v.warnings), 0)

    def test_emails_valid(self):
        emails = [{'sub': 'Hello', 'body': 'World'}]
        result = self.v.validate_emails(emails)
        self.assertEqual(len(result), 1)

    def test_emails_missing_sub(self):
        emails = [{'body': 'Only body'}]
        result = self.v.validate_emails(emails)
        self.assertEqual(len(result), 0)

    def test_gov_intel_valid_types(self):
        gov = {'types': [['g00', 'Pass', 500, 3]], 'domains': ['gov.test']}
        result = self.v.validate_gov_intel(gov)
        self.assertIn('types', result)
        self.assertEqual(len(self.v.errors), 0)

    def test_gov_intel_bad_type_entry(self):
        gov = {'types': ['not_a_list'], 'domains': []}
        self.v.validate_gov_intel(gov)
        self.assertGreater(len(self.v.errors), 0)

    def test_gov_intel_not_dict(self):
        result = self.v.validate_gov_intel([])
        self.assertGreater(len(self.v.errors), 0)
        self.assertIn('types', result)
        self.assertIn('domains', result)

    def test_report_has_errors(self):
        self.v.error('something broke')
        self.assertTrue(self.v.report())

    def test_report_no_errors(self):
        self.assertFalse(self.v.report())


if __name__ == '__main__':
    unittest.main()
