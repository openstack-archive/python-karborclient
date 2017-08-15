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

from karborclient.osc.v1 import plans as osc_plans
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import plans


PLAN_INFO = {
    "status": "suspended",
    "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
    "description": "",
    "parameters": {},
    "id": "204c825e-eb2f-4609-95ab-70b3caa43ac8",
    "resources": [{
        'type': 'OS::Cinder::Volume',
        'id': '71bfe64a-e0b9-4a91-9e15-a7fc9ab31b14',
        'name': 'testsinglevolume'}],
    "name": "OS Volume protection plan."
}


class TestPlans(fakes.TestDataProtection):
    def setUp(self):
        super(TestPlans, self).setUp()
        self.plans_mock = self.app.client_manager.data_protection.plans
        self.plans_mock.reset_mock()


class TestListPlans(TestPlans):
    def setUp(self):
        super(TestListPlans, self).setUp()
        self.plans_mock.list.return_value = [plans.Plan(
            None, copy.deepcopy(PLAN_INFO))]

        # Command to test
        self.cmd = osc_plans.ListPlans(self.app, None)

    def test_plans_list(self):
        arglist = ['--status', 'suspended']
        verifylist = [('status', 'suspended')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            ['Id', 'Name', 'Description', 'Provider id', 'Status'])
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [("204c825e-eb2f-4609-95ab-70b3caa43ac8",
                          "OS Volume protection plan.",
                          "",
                          "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
                          "suspended")]
        self.assertEqual(expected_data, list(data))


class TestCreatePlan(TestPlans):
    def setUp(self):
        super(TestCreatePlan, self).setUp()
        self.plans_mock.create.return_value = plans.Plan(
            None, copy.deepcopy(PLAN_INFO))
        # Command to test
        self.cmd = osc_plans.CreatePlan(self.app, None)

    def test_plan_create(self):
        arglist = ['OS Volume protection plan.',
                   'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
                   "'71bfe64a-e0b9-4a91-9e15-a7fc9ab31b14'="
                   "'OS::Cinder::Volume'='testsinglevolume'"]
        verifylist = [('name', 'OS Volume protection plan.'),
                      ('provider_id', 'cf56bd3e-97a7-4078-b6d5-f36246333fd9'),
                      ('resources', "'71bfe64a-e0b9-4a91-9e15-a7fc9ab31b14'="
                                    "'OS::Cinder::Volume'='testsinglevolume'")]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.plans_mock.create.assert_called_once_with(
            'OS Volume protection plan.',
            'cf56bd3e-97a7-4078-b6d5-f36246333fd9',
            [{'id': "'71bfe64a-e0b9-4a91-9e15-a7fc9ab31b14'",
              'type': "'OS::Cinder::Volume'",
              'name': "'testsinglevolume'"}],
            {}, description=None)


class TestUpdatePlan(TestPlans):
    def setUp(self):
        super(TestUpdatePlan, self).setUp()
        self.plans_mock.get.return_value = plans.Plan(
            None, copy.deepcopy(PLAN_INFO))
        self.plans_mock.update.return_value = plans.Plan(
            None, copy.deepcopy(PLAN_INFO))
        # Command to test
        self.cmd = osc_plans.UpdatePlan(self.app, None)

    def test_plan_update(self):
        arglist = ['204c825e-eb2f-4609-95ab-70b3caa43ac8',
                   '--status', 'started']
        verifylist = [('plan_id', '204c825e-eb2f-4609-95ab-70b3caa43ac8'),
                      ('status', 'started')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.plans_mock.update.assert_called_once_with(
            '204c825e-eb2f-4609-95ab-70b3caa43ac8',
            {'status': 'started'})


class TestDeletePlan(TestPlans):
    def setUp(self):
        super(TestDeletePlan, self).setUp()
        self.plans_mock.get.return_value = plans.Plan(
            None, copy.deepcopy(PLAN_INFO))
        # Command to test
        self.cmd = osc_plans.DeletePlan(self.app, None)

    def test_plan_delete(self):
        arglist = ['204c825e-eb2f-4609-95ab-70b3caa43ac8']
        verifylist = [('plan', ['204c825e-eb2f-4609-95ab-70b3caa43ac8'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.plans_mock.delete.assert_called_once_with(
            '204c825e-eb2f-4609-95ab-70b3caa43ac8')


class TestShowPlan(TestPlans):
    def setUp(self):
        super(TestShowPlan, self).setUp()
        self._plan_info = copy.deepcopy(PLAN_INFO)
        self.plans_mock.get.return_value = plans.Plan(
            None, self._plan_info)

        # Command to test
        self.cmd = osc_plans.ShowPlan(self.app, None)

    def test_plan_show(self):
        arglist = ['204c825e-eb2f-4609-95ab-70b3caa43ac8']
        verifylist = [('plan', '204c825e-eb2f-4609-95ab-70b3caa43ac8')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = (
            'description', 'id', 'name', 'parameters', 'provider_id',
            'resources', 'status')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        self.assertEqual(self._plan_info['description'], data[0])
        self.assertEqual(self._plan_info['id'], data[1])
        self.assertEqual(self._plan_info['name'], data[2])
        self.assertEqual(self._plan_info['parameters'], data[3])
        self.assertEqual(self._plan_info['provider_id'], data[4])
        self.assertEqual(self._plan_info['resources'], data[5])
        self.assertEqual(self._plan_info['status'], data[6])
