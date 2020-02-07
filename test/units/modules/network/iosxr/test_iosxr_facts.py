# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json

from units.compat.mock import patch
from units.modules.utils import set_module_args
from .iosxr_module import TestIosxrModule, load_fixture
from ansible.modules.network.iosxr import iosxr_facts


class TestIosxrFacts(TestIosxrModule):

    module = iosxr_facts

    def setUp(self):
        super(TestIosxrFacts, self).setUp()

        self.mock_run_commands = patch(
            'ansible.module_utils.network.iosxr.facts.legacy.base.run_commands')
        self.run_commands = self.mock_run_commands.start()

        self.mock_get_resource_connection = patch('ansible.module_utils.network.common.facts.facts.get_resource_connection')
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_capabilities = patch('ansible.module_utils.network.iosxr.facts.legacy.base.get_capabilities')
        self.get_capabilities = self.mock_get_capabilities.start()
        self.get_capabilities.return_value = {
            'device_info': {
                'network_os': 'iosxr',
                'network_os_hostname': 'iosxr01',
                'network_os_image': 'bootflash:disk0/xrvr-os-mbi-6.1.3/mbixrvr-rp.vm',
                'network_os_version': '6.1.3[Default]'
            },
            'network_api': 'cliconf'
        }

    def tearDown(self):
        super(TestIosxrFacts, self).tearDown()

        self.mock_run_commands.stop()
        self.mock_get_capabilities.stop()
        self.mock_get_resource_connection.stop()

    def load_fixtures(self, commands=None):

        def load_from_file(*args, **kwargs):
            module, commands = args
            output = list()

            for item in commands:
                try:
                    obj = json.loads(item)
                    command = obj['command']
                except ValueError:
                    command = item
                filename = str(command).replace(' ', '_')
                filename = filename.replace('/', '7')
                filename = filename.replace('|', '_')
                output.append(load_fixture(filename))
            return output

        self.run_commands.side_effect = load_from_file

    def test_iosxr_facts_gather_subset_default(self):
        set_module_args(dict())
        result = self.execute_module()
        ansible_facts = result['ansible_facts']
        self.assertIn('hardware', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('default', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('interfaces', ansible_facts['ansible_net_gather_subset'])
        self.assertEqual('iosxr01', ansible_facts['ansible_net_hostname'])
        self.assertEqual(['disk0:', 'flash0:'], ansible_facts['ansible_net_filesystems'])
        self.assertIn('GigabitEthernet0/0/0/0', ansible_facts['ansible_net_interfaces'].keys())
        self.assertEqual('3095', ansible_facts['ansible_net_memtotal_mb'])
        self.assertEqual('1499', ansible_facts['ansible_net_memfree_mb'])

    def test_iosxr_facts_gather_subset_config(self):
        set_module_args({'gather_subset': 'config'})
        result = self.execute_module()
        ansible_facts = result['ansible_facts']
        self.assertIn('default', ansible_facts['ansible_net_gather_subset'])
        self.assertIn('config', ansible_facts['ansible_net_gather_subset'])
        self.assertEqual('iosxr01', ansible_facts['ansible_net_hostname'])
        self.assertIn('ansible_net_config', ansible_facts)
