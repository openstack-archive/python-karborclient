# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from karborclient.osc.v1 import providers as osc_providers
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import providers


PROVIDER_INFO = {
    "id": "2220f8b1-975d-4621-a872-fa9afb43cb6c",
    "name": "OS Infra Provider",
    "description": "provider description",
    "extended_info_schema": {
        "options_schema": {
            "OS::Cinder::Volume": {
                "required": [
                    "backup_mode"
                ],
                "type": "object",
                "properties": {
                    "backup_mode": {
                        "default": "auto",
                        "enum": [
                            "full",
                            "incremental",
                            "auto"
                        ],
                        "type": "string",
                        "description": "The backup mode.",
                        "title": "Backup Mode"
                    }
                },
                "title": "Cinder Protection Options"
            }
        },
        "saved_info_schema": {
            "OS::Cinder::Volume": {
                "required": [
                    "name"
                ],
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name for this backup.",
                        "title": "Name"
                    }
                },
                "title": "Cinder Protection Saved Info"
            }
        },
        "restore_schema": {
            "OS::Cinder::Volume": {
                "type": "object",
                "properties": {
                    "restore_name": {
                        "type": "string",
                        "description": "The name of the restored volume.",
                        "title": "Restore Name"
                    }
                },
                "title": "Cinder Protection Restore"
            }
        }
    }
}


class TestProviders(fakes.TestDataProtection):
    def setUp(self):
        super(TestProviders, self).setUp()
        self.providers_mock = self.app.client_manager.data_protection.providers
        self.providers_mock.reset_mock()


class TestListProviders(TestProviders):
    def setUp(self):
        super(TestListProviders, self).setUp()
        self.providers_mock.list.return_value = [providers.Provider(
            None, copy.deepcopy(PROVIDER_INFO))]

        # Command to test
        self.cmd = osc_providers.ListProviders(self.app, None)

    def test_providers_list(self):
        arglist = ['--name', 'OS Infra Provider']
        verifylist = [('name', 'OS Infra Provider')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Name', 'Description'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("2220f8b1-975d-4621-a872-fa9afb43cb6c",
                          "OS Infra Provider",
                          "provider description")]
        self.assertEqual(expected_data, list(data))


class TestShowProvider(TestProviders):
    def setUp(self):
        super(TestShowProvider, self).setUp()
        self._provider_info = copy.deepcopy(PROVIDER_INFO)
        self.providers_mock.get.return_value = providers.Provider(
            None, self._provider_info)

        # Command to test
        self.cmd = osc_providers.ShowProvider(self.app, None)

    def test_provider_show(self):
        arglist = ['2220f8b1-975d-4621-a872-fa9afb43cb6c']
        verifylist = [('provider', '2220f8b1-975d-4621-a872-fa9afb43cb6c')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'description', 'extended_info_schema', 'id', 'name')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._provider_info['description'], data[0])
        self.assertEqual(self._provider_info['extended_info_schema'], data[1])
        self.assertEqual(self._provider_info['id'], data[2])
        self.assertEqual(self._provider_info['name'], data[3])
