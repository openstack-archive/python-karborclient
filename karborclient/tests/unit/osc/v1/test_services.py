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

from karborclient.osc.v1 import services as osc_services
from karborclient.tests.unit.osc.v1 import fakes
from karborclient.v1 import services

SERVICE_INFO = {
    "status": "enabled",
    "binary": "karbor-operationengine",
    "state": "up",
    "updated_at": "2017-10-25T07:06:58.000000",
    "host": "fake_host",
    "disabled_reason": None,
    "id": 1
}


class TestServices(fakes.TestDataProtection):
    def setUp(self):
        super(TestServices, self).setUp()
        self.services_mock = self.app.client_manager.data_protection.services
        self.services_mock.reset_mock()


class TestListServices(TestServices):
    def setUp(self):
        super(TestListServices, self).setUp()
        self.services_mock.list.return_value = [
            services.Service(None, copy.deepcopy(SERVICE_INFO))]
        self.cmd = osc_services.ListServices(self.app, None)

    def test_services_list(self):
        arg_list = ['--host', 'fake_host']
        verify_list = [('host', 'fake_host')]

        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        columns, data = self.cmd.take_action(parsed_args)
        expected_columns = (["Id", "Binary", "Host", "Status", "State",
                             "Updated_at", "Disabled Reason"])
        self.assertEqual(expected_columns, columns)
        expected_data = [(1,
                          "karbor-operationengine",
                          "fake_host",
                          "enabled",
                          "up",
                          "2017-10-25T07:06:58.000000",
                          None
                          )]
        self.assertEqual(expected_data, list(data))


class TestEnableService(TestServices):
    def setUp(self):
        super(TestEnableService, self).setUp()
        self.services_mock.enable.return_value = services.Service(
            None, copy.deepcopy(SERVICE_INFO))
        self.cmd = osc_services.EnableService(self.app, None)

    def test_enable_service(self):
        arg_list = ['1']
        verify_list = [('service_id', '1')]
        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        self.cmd.take_action(parsed_args)
        self.services_mock.enable.assert_called_once_with('1')


class TestDisableService(TestServices):
    def setUp(self):
        super(TestDisableService, self).setUp()
        self.services_mock.disable.return_value = services.Service(
            None, copy.deepcopy(SERVICE_INFO))
        self.services_mock.disable_log_reason.return_value = services.Service(
            None, copy.deepcopy(SERVICE_INFO))
        self.cmd = osc_services.DisableService(self.app, None)

    def test_disable_service(self):
        arg_list = ['1']
        verify_list = [('service_id', '1')]
        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        self.cmd.take_action(parsed_args)
        self.services_mock.disable.assert_called_once_with('1')

    def test_disable_service_with_reason(self):
        arg_list = ['1', '--reason', 'fake_reason']
        verify_list = [('service_id', '1'), ('reason', 'fake_reason')]
        parsed_args = self.check_parser(self.cmd, arg_list, verify_list)
        self.cmd.take_action(parsed_args)
        self.services_mock.disable_log_reason.assert_called_once_with(
            '1', 'fake_reason')
