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

from karborclient.osc.v1 import verifications as osc_verifications
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import verifications


VERIFICATION_INFO = {
    "id": "22b82aa7-9179-4c71-bba2-caf5c0e68db7",
    "project_id": "e486a2f49695423ca9c47e589b948108",
    "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
    "checkpoint_id": "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
    "parameters": {},
    "resources_status": {},
    "resources_reason": {},
    "status": "success"
}


class TestVerifications(fakes.TestDataProtection):
    def setUp(self):
        super(TestVerifications, self).setUp()
        self.verifications_mock = (
            self.app.client_manager.data_protection.verifications)
        self.verifications_mock.reset_mock()


class TestListVerifications(TestVerifications):
    def setUp(self):
        super(TestListVerifications, self).setUp()
        self.verifications_mock.list.return_value = (
            [verifications.Verification(
                None, copy.deepcopy(VERIFICATION_INFO))])

        # Command to test
        self.cmd = osc_verifications.ListVerifications(self.app, None)

    def test_verifications_list(self):
        arglist = ['--status', 'success']
        verifylist = [('status', 'success')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            ['Id', 'Project id', 'Provider id', 'Checkpoint id',
             'Parameters', 'Status'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("22b82aa7-9179-4c71-bba2-caf5c0e68db7",
                          "e486a2f49695423ca9c47e589b948108",
                          "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
                          "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
                          jsonutils.dumps({}),
                          "success")]
        self.assertEqual(expected_data, list(data))


class TestCreateVerification(TestVerifications):
    def setUp(self):
        super(TestCreateVerification, self).setUp()
        self.verifications_mock.create.return_value = (
            verifications.Verification(
                None, copy.deepcopy(VERIFICATION_INFO)))
        self.cmd = osc_verifications.CreateVerification(self.app, None)

    def test_verification_create(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint_id',
                       'dcb20606-ad71-40a3-80e4-ef0fafdad0c3')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.verifications_mock.create.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3', {})


class TestShowVerification(TestVerifications):
    def setUp(self):
        super(TestShowVerification, self).setUp()
        self._verification_info = copy.deepcopy(VERIFICATION_INFO)
        self.verifications_mock.get.return_value = (
            verifications.Verification(None, self._verification_info))

        self.cmd = osc_verifications.ShowVerification(self.app, None)

    def test_verification_show(self):
        arglist = ['22b82aa7-9179-4c71-bba2-caf5c0e68db7']
        verifylist = [('verification', '22b82aa7-9179-4c71-bba2-caf5c0e68db7')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'checkpoint_id', 'id', 'parameters', 'project_id',
            'provider_id', 'resources_reason', 'resources_status',
            'status')
        self.assertEqual(expected_columns, columns)

        self.assertEqual(self._verification_info['checkpoint_id'], data[0])
        self.assertEqual(self._verification_info['id'], data[1])
        self.assertEqual(self._verification_info['parameters'], data[2])
        self.assertEqual(self._verification_info['project_id'], data[3])
        self.assertEqual(self._verification_info['provider_id'], data[4])
        self.assertEqual(self._verification_info['resources_reason'], data[5])
        self.assertEqual(self._verification_info['resources_status'], data[6])
        self.assertEqual(self._verification_info['status'], data[7])
