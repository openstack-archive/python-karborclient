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

from oslo_serialization import jsonutils

from karborclient.osc.v1 import restores as osc_restores
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import restores


RESTORE_INFO = {
    "id": "22b82aa7-9179-4c71-bba2-caf5c0e68db7",
    "project_id": "e486a2f49695423ca9c47e589b948108",
    "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
    "checkpoint_id": "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
    "restore_target": "",
    "parameters": {},
    "restore_auth": {},
    "resources_status": {},
    "resources_reason": {},
    "status": "success"
}


class TestRestores(fakes.TestDataProtection):
    def setUp(self):
        super(TestRestores, self).setUp()
        self.restores_mock = self.app.client_manager.data_protection.restores
        self.restores_mock.reset_mock()


class TestListRestores(TestRestores):
    def setUp(self):
        super(TestListRestores, self).setUp()
        self.restores_mock.list.return_value = [restores.Restore(
            None, copy.deepcopy(RESTORE_INFO))]

        # Command to test
        self.cmd = osc_restores.ListRestores(self.app, None)

    def test_restores_list(self):
        arglist = ['--status', 'success']
        verifylist = [('status', 'success')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Project id', 'Provider id', 'Checkpoint id',
             'Restore target', 'Parameters', 'Status'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("22b82aa7-9179-4c71-bba2-caf5c0e68db7",
                          "e486a2f49695423ca9c47e589b948108",
                          "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
                          "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
                          "",
                          jsonutils.dumps({}),
                          "success")]
        self.assertEqual(expected_data, list(data))


class TestCreateRestore(TestRestores):
    def setUp(self):
        super(TestCreateRestore, self).setUp()
        self.restores_mock.create.return_value = restores.Restore(
            None, copy.deepcopy(RESTORE_INFO))
        # Command to test
        self.cmd = osc_restores.CreateRestore(self.app, None)

    def test_restore_create(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint_id',
                       'dcb20606-ad71-40a3-80e4-ef0fafdad0c3')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.restores_mock.create.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3',
            None, {}, None)


class TestShowRestore(TestRestores):
    def setUp(self):
        super(TestShowRestore, self).setUp()
        self._restore_info = copy.deepcopy(RESTORE_INFO)
        self.restores_mock.get.return_value = restores.Restore(
            None, self._restore_info)

        # Command to test
        self.cmd = osc_restores.ShowRestore(self.app, None)

    def test_restore_show(self):
        arglist = ['22b82aa7-9179-4c71-bba2-caf5c0e68db7']
        verifylist = [('restore', '22b82aa7-9179-4c71-bba2-caf5c0e68db7')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'checkpoint_id', 'id', 'parameters', 'project_id',
            'provider_id', 'resources_reason', 'resources_status',
            'restore_auth', 'restore_target', 'status')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._restore_info['checkpoint_id'], data[0])
        self.assertEqual(self._restore_info['id'], data[1])
        self.assertEqual(self._restore_info['parameters'], data[2])
        self.assertEqual(self._restore_info['project_id'], data[3])
        self.assertEqual(self._restore_info['provider_id'], data[4])
        self.assertEqual(self._restore_info['resources_reason'], data[5])
        self.assertEqual(self._restore_info['resources_status'], data[6])
        self.assertEqual(self._restore_info['restore_auth'], data[7])
        self.assertEqual(self._restore_info['restore_target'], data[8])
        self.assertEqual(self._restore_info['status'], data[9])
