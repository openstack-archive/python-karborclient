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

from karborclient.osc.v1 import checkpoints as osc_checkpoints
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import checkpoints


CHECKPOINT_INFO = {
    "id": "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
    "project_id": "e486a2f49695423ca9c47e589b948108",
    "status": "available",
    "protection_plan": {
        "id": "3523a271-68aa-42f5-b9ba-56e5200a2ebb",
        "name": "My application",
        "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
        "resources": [{
            "id": "99777fdd-8a5b-45ab-ba2c-52420008103f",
            "type": "OS::Glance::Image",
            "name": "cirros-0.3.4-x86_64-uec"}]
    },
    "resource_graph": jsonutils.dumps(
        "[{'0x0': ['OS::Glance::Image', "
        "'99777fdd-8a5b-45ab-ba2c-52420008103f', "
        "'cirros-0.3.4-x86_64-uec']}, [[['0x0']]]]"
    ),
}

CHECKPOINT_INFO_2 = {
    "id": "a6fd95fe-0892-43b2-ad3c-e56f3a1b86b8",
    "project_id": "79b35e99a6a541b3bcede40f590d6878",
    "status": "available",
    "protection_plan": {
        "id": "3b47fd5d-21f9-4e63-8409-0acb1bffc038",
        "name": "My application",
        "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
        "resources": [{
            "id": "99777fdd-8a5b-45ab-ba2c-52420008103f",
            "type": "OS::Glance::Image",
            "name": "cirros-0.3.4-x86_64-uec"}]
    },
    "resource_graph": jsonutils.dumps(
        "[{'0x0': ['OS::Glance::Image', "
        "'99777fdd-8a5b-45ab-ba2c-52420008103f', "
        "'cirros-0.3.4-x86_64-uec']}, [[['0x0']]]]"
    ),
}


class TestCheckpoints(fakes.TestDataProtection):
    def setUp(self):
        super(TestCheckpoints, self).setUp()
        cm = self.app.client_manager
        self.checkpoints_mock = cm.data_protection.checkpoints
        self.checkpoints_mock.reset_mock()


class TestListCheckpoints(TestCheckpoints):
    def setUp(self):
        super(TestListCheckpoints, self).setUp()

        # Command to test
        self.cmd = osc_checkpoints.ListCheckpoints(self.app, None)

    def test_checkpoints_list(self):
        self.checkpoints_mock.list.return_value = [checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO))]
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Project id', 'Status', 'Protection plan', 'Metadata',
             'Created at'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [(
            "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
            "e486a2f49695423ca9c47e589b948108",
            "available",
            "Name: %(name)s\nId: %(id)s" % {
                "id": "3523a271-68aa-42f5-b9ba-56e5200a2ebb",
                "name": "My application",
            },
            '',
            '')]
        self.assertEqual(expected_data, list(data))

    def test_checkpoints_list_with_all_projects(self):
        self.checkpoints_mock.list.return_value = [checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO)), checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO_2))]
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9', '--all-projects']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('all_projects', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            ['Id', 'Project id', 'Status', 'Protection plan', 'Metadata',
             'Created at'])
        self.assertEqual(expected_columns, columns)

        expected_data = [(
            "dcb20606-ad71-40a3-80e4-ef0fafdad0c3",
            "e486a2f49695423ca9c47e589b948108",
            "available",
            "Name: %(name)s\nId: %(id)s" % {
                "id": "3523a271-68aa-42f5-b9ba-56e5200a2ebb",
                "name": "My application",
            },
            '',
            ''), (
            "a6fd95fe-0892-43b2-ad3c-e56f3a1b86b8",
            "79b35e99a6a541b3bcede40f590d6878",
            "available",
            "Name: %(name)s\nId: %(id)s" % {
                "id": "3b47fd5d-21f9-4e63-8409-0acb1bffc038",
                "name": "My application",
            },
            '',
            '')
        ]
        self.assertEqual(expected_data, list(data))


class TestCreateCheckpoint(TestCheckpoints):
    def setUp(self):
        super(TestCreateCheckpoint, self).setUp()
        self.checkpoints_mock.create.return_value = checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO))
        # Command to test
        self.cmd = osc_checkpoints.CreateCheckpoint(self.app, None)

    def test_checkpoint_create(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   '3523a271-68aa-42f5-b9ba-56e5200a2ebb']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('plan_id', '3523a271-68aa-42f5-b9ba-56e5200a2ebb')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.checkpoints_mock.create.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            '3523a271-68aa-42f5-b9ba-56e5200a2ebb',
            None)


class TestShowCheckpoint(TestCheckpoints):
    def setUp(self):
        super(TestShowCheckpoint, self).setUp()
        self.checkpoints_mock.get.return_value = checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO))
        # Command to test
        self.cmd = osc_checkpoints.ShowCheckpoint(self.app, None)

    def test_checkpoint_show(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint_id',
                       'dcb20606-ad71-40a3-80e4-ef0fafdad0c3')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.checkpoints_mock.get.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3')


class TestDeleteCheckpoint(TestCheckpoints):
    def setUp(self):
        super(TestDeleteCheckpoint, self).setUp()
        self.checkpoints_mock.get.return_value = checkpoints.Checkpoint(
            None, copy.deepcopy(CHECKPOINT_INFO))
        # Command to test
        self.cmd = osc_checkpoints.DeleteCheckpoint(self.app, None)

    def test_checkpoint_delete(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint',
                       ['dcb20606-ad71-40a3-80e4-ef0fafdad0c3'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.checkpoints_mock.delete.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3')


class TestResetCheckpointState(TestCheckpoints):
    def setUp(self):
        super(TestResetCheckpointState, self).setUp()
        self.cmd = osc_checkpoints.ResetCheckpointState(self.app, None)

    def test_reset_checkpoint_with_default_state(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint',
                       ['dcb20606-ad71-40a3-80e4-ef0fafdad0c3']),
                      ('state', 'error')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.checkpoints_mock.reset_state.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3',
            'error')

    def test_reset_checkpoint(self):
        arglist = ['cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   'dcb20606-ad71-40a3-80e4-ef0fafdad0c3',
                   '--available']
        verifylist = [('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('checkpoint',
                       ['dcb20606-ad71-40a3-80e4-ef0fafdad0c3']),
                      ('state', 'available')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.checkpoints_mock.reset_state.assert_called_once_with(
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            'dcb20606-ad71-40a3-80e4-ef0fafdad0c3',
            'available')
