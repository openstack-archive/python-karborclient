#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import fixtures
import mock

from karborclient import shell
from karborclient.tests.unit import base
from karborclient.tests.unit.v1 import fakes

FAKE_PROVIDER_ID = '1234'
FAKE_ENDPOINT = 'http://127.0.0.1/identity'


class ShellFixture(fixtures.Fixture):
    def setUp(self):
        super(ShellFixture, self).setUp()
        self.shell = shell.KarborShell()

    def tearDown(self):
        # For some method like test_image_meta_bad_action we are
        # testing a SystemExit to be thrown and object self.shell has
        # no time to get instantiated which is OK in this case, so
        # we make sure the method is there before launching it.
        if hasattr(self.shell, 'cs'):
            self.shell.cs.clear_callstack()
        super(ShellFixture, self).tearDown()


class ShellTest(base.TestCaseShell):

    FAKE_ENV = {
        'OS_USERNAME': 'username',
        'OS_PASSWORD': 'password',
        'OS_TENANT_NAME': 'project_id',
        'OS_AUTH_URL': 'http://no.where/v2.0',
        'OS_AUTH_TOKEN': 'fake_token'
    }

    def setUp(self):
        """Run before each test."""
        super(ShellTest, self).setUp()
        for var in self.FAKE_ENV:
            self.useFixture(fixtures.EnvironmentVariable(
                var, self.FAKE_ENV[var]))
        self.shell = self.useFixture(ShellFixture()).shell

        get_endpoint = mock.MagicMock()
        get_endpoint.return_value = FAKE_ENDPOINT
        self.useFixture(fixtures.MonkeyPatch(
            'keystoneauth1.identity.generic.token.Token.get_endpoint',
            get_endpoint))
        self.useFixture(fixtures.MonkeyPatch('karborclient.client.Client',
                                             fakes.FakeClient))
        self.useFixture(fixtures.MonkeyPatch(
            'karborclient.common.http._construct_http_client',
            fakes.FakeHTTPClient))

    def run_command(self, cmd):
        if not isinstance(cmd, list):
            cmd = cmd.split()
        self.shell.main(cmd)

    def assert_called(self, method, url, body=None, **kwargs):
        return self.shell.cs.assert_called(method, url, body, **kwargs)

    def test_checkpoint_list_with_all_tenants(self):
        self.run_command(
            'checkpoint-list ' + FAKE_PROVIDER_ID + ' --all-tenants 1')

        self.assert_called('GET',
                           '/providers/1234/'
                           'checkpoints?all_tenants=1')

    def test_checkpoint_list_with_all(self):
        self.run_command(
            'checkpoint-list ' + FAKE_PROVIDER_ID + ' --all')
        self.assert_called('GET',
                           '/providers/1234/'
                           'checkpoints?all_tenants=1')

    def test_plan_list_with_all_tenants(self):
        self.run_command('plan-list --all-tenants 1')
        self.assert_called('GET', '/plans?all_tenants=1')

    def test_plan_list_with_all(self):
        self.run_command('plan-list --all')
        self.assert_called('GET', '/plans?all_tenants=1')

    def test_resotre_list_with_all_tenants(self):
        self.run_command('restore-list --all-tenants 1')
        self.assert_called('GET', '/restores?all_tenants=1')

    def test_resotre_list_with_all(self):
        self.run_command('restore-list --all')
        self.assert_called('GET', '/restores?all_tenants=1')

    def test_verification_list_with_all_tenants(self):
        self.run_command('verification-list --all-tenants 1')
        self.assert_called('GET', '/verifications?all_tenants=1')

    def test_verification_list_with_all(self):
        self.run_command('verification-list --all')
        self.assert_called('GET', '/verifications?all_tenants=1')

    def test_trigger_list_with_all_tenants(self):
        self.run_command('trigger-list --all-tenants 1')
        self.assert_called('GET', '/triggers?all_tenants=1')

    def test_trigger_list_with_all(self):
        self.run_command('trigger-list --all')
        self.assert_called('GET', '/triggers?all_tenants=1')

    def test_scheduledoperation_list_with_all_tenants(self):
        self.run_command('scheduledoperation-list --all-tenants 1')
        self.assert_called('GET', '/scheduled_operations?all_tenants=1')

    def test_scheduledoperation_list_with_all(self):
        self.run_command('scheduledoperation-list --all')
        self.assert_called('GET', '/scheduled_operations?all_tenants=1')

    def test_operationlog_list_with_all_tenants(self):
        self.run_command('operationlog-list --all-tenants 1')
        self.assert_called('GET', '/operation_logs?all_tenants=1')

    def test_operationlog_list_with_all(self):
        self.run_command('operationlog-list --all')
        self.assert_called('GET', '/operation_logs?all_tenants=1')
