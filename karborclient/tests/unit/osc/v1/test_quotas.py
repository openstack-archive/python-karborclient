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

from karborclient.osc.v1 import quotas as osc_quotas
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import quotas


QUOTA_INFO = {
    "id": "73f74f90a1754bd7ad658afb3272323f",
    "plans": "40"
}


class TestQuotas(fakes.TestDataProtection):
    def setUp(self):
        super(TestQuotas, self).setUp()
        self.quotas_mock = self.app.client_manager.data_protection.quotas
        self.quotas_mock.reset_mock()


class TestUpdateQuotas(TestQuotas):
    def setUp(self):
        super(TestUpdateQuotas, self).setUp()
        self.quotas_mock.update.return_value = quotas.Quota(
            None, copy.deepcopy(QUOTA_INFO))
        self.cmd = osc_quotas.UpdateQuotas(self.app, None)

    def test_quotas_update(self):
        arglist = ['--plans',
                   '40', '73f74f90a1754bd7ad658afb3272323f']
        verifylist = [('plans', 40),
                      ('tenant',
                       '73f74f90a1754bd7ad658afb3272323f')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.quotas_mock.update.assert_called_once_with(
            '73f74f90a1754bd7ad658afb3272323f',
            {'plans': 40})


class TestShowQuotas(TestQuotas):
    def setUp(self):
        super(TestShowQuotas, self).setUp()
        self._quota_info = copy.deepcopy(QUOTA_INFO)
        self.quotas_mock.get.return_value = quotas.Quota(
            None, copy.deepcopy(QUOTA_INFO))

        self.cmd = osc_quotas.ShowQuotas(self.app, None)

    def test_quota_show(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('id', 'plans'), columns)
        self.assertEqual(('73f74f90a1754bd7ad658afb3272323f', '40'),
                         data)
