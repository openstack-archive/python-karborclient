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

from karborclient.osc.v1 import quota_classes as osc_quota_classes
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import quota_classes


QUOTA_CLASSES_INFO = {
    "id": "default",
    "plans": "40"
}


class TestQuotaClasses(fakes.TestDataProtection):
    def setUp(self):
        super(TestQuotaClasses, self).setUp()
        self.quotas_mock = (
            self.app.client_manager.data_protection.quota_classes)
        self.quotas_mock.reset_mock()


class TestUpdateQuotaClasses(TestQuotaClasses):
    def setUp(self):
        super(TestUpdateQuotaClasses, self).setUp()
        self.quotas_mock.update.return_value = quota_classes.QuotaClass(
            None, copy.deepcopy(QUOTA_CLASSES_INFO))
        self.cmd = osc_quota_classes.UpdateQuotaClasses(self.app, None)

    def test_quota_classes_update(self):
        arglist = ['--plans',
                   '40', 'default']
        verifylist = [('plans', 40),
                      ('class_name',
                       'default')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.quotas_mock.update.assert_called_once_with(
            'default',
            {'plans': 40})


class TestShowQuotaClasses(TestQuotaClasses):
    def setUp(self):
        super(TestShowQuotaClasses, self).setUp()
        self._quota_info = copy.deepcopy(QUOTA_CLASSES_INFO)
        self.quotas_mock.get.return_value = quota_classes.QuotaClass(
            None, copy.deepcopy(QUOTA_CLASSES_INFO))

        self.cmd = osc_quota_classes.ShowQuotaClasses(self.app, None)

    def test_quota_classes_show(self):
        arglist = ['default']
        verifylist = [('class_name', 'default')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(('id', 'plans'), columns)
        self.assertEqual(('default', '40'),
                         data)
