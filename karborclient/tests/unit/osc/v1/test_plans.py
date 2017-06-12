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

from karborclient.osc.v1 import plans as osc_plans
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import plans


PLAN_INFO = {
    "status": "suspended",
    "provider_id": "cf56bd3e-97a7-4078-b6d5-f36246333fd9",
    "description": "",
    "parameters": {},
    "id": "204c825e-eb2f-4609-95ab-70b3caa43ac8",
    "resources": [],
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
            None, PLAN_INFO)]

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
