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

import logging
import re
import sys

import fixtures
from keystoneclient import fixture
from keystoneclient.fixture import v2 as ks_v2_fixture
import mock
from oslo_log import handlers
from oslo_log import log
import six
from testtools import matchers

from smaugclient.openstack.common.apiclient import exceptions
import smaugclient.shell
from smaugclient.tests.unit import base


FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV2 = {'OS_USERNAME': 'username',
             'OS_PASSWORD': 'password',
             'OS_TENANT_ID': 'tenant_id',
             'OS_AUTH_URL': 'http://no.where/v2.0'}

FAKE_ENV_v3 = {'OS_USERNAME': 'username',
               'OS_PASSWORD': 'password',
               'OS_TENANT_ID': 'tenant_id',
               'OS_USER_DOMAIN_NAME': 'domain_name',
               'OS_AUTH_URL': 'http://no.where/v3'}


def _create_ver_list(versions):
    return {'versions': {'values': versions}}


class TestArgs(object):
    package_version = ''
    smaug_repo_url = 'http://127.0.0.1'
    exists_action = ''
    is_public = False
    categories = []


class ShellTest(base.TestCaseShell):

    def make_env(self, exclude=None, fake_env=FAKE_ENV):
        env = dict((k, v) for k, v in fake_env.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))


class ShellCommandTest(ShellTest):

    _msg_no_tenant_project = ('You must provide a project name or project'
                              ' id via --os-project-name, --os-project-id,'
                              ' env[OS_PROJECT_ID] or env[OS_PROJECT_NAME].'
                              ' You may use os-project and os-tenant'
                              ' interchangeably.',)

    def setUp(self):
        super(ShellCommandTest, self).setUp()

        def get_auth_endpoint(bound_self, args):
            return ('test', {})
        self.useFixture(fixtures.MonkeyPatch(
            'smaugclient.shell.SmaugShell._get_endpoint_and_kwargs',
            get_auth_endpoint))
        self.client = mock.MagicMock()

        # To prevent log descriptors from being closed during
        # shell tests set a custom StreamHandler
        self.logger = log.getLogger(None).logger
        self.logger.level = logging.DEBUG
        self.color_handler = handlers.ColorHandler(sys.stdout)
        self.logger.addHandler(self.color_handler)

    def tearDown(self):
        super(ShellTest, self).tearDown()
        self.logger.removeHandler(self.color_handler)

    def shell(self, argstr, exitcodes=(0,)):
        orig = sys.stdout
        orig_stderr = sys.stderr
        try:
            sys.stdout = six.StringIO()
            sys.stderr = six.StringIO()
            _shell = smaugclient.shell.SmaugShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertIn(exc_value.code, exitcodes)
        finally:
            stdout = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
            stderr = sys.stderr.getvalue()
            sys.stderr.close()
            sys.stderr = orig_stderr
        return (stdout, stderr)

    def register_keystone_discovery_fixture(self, mreq):
        v2_url = "http://no.where/v2.0"
        v2_version = fixture.V2Discovery(v2_url)
        mreq.register_uri('GET', v2_url, json=_create_ver_list([v2_version]),
                          status_code=200)

    def register_keystone_token_fixture(self, mreq):
        v2_token = ks_v2_fixture.Token(token_id='token')
        service = v2_token.add_service('application-catalog')
        service.add_endpoint('http://no.where', region='RegionOne')
        mreq.register_uri('POST',
                          'http://no.where/v2.0/tokens',
                          json=v2_token,
                          status_code=200)

    def test_help_unknown_command(self):
        self.assertRaises(exceptions.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: smaug',
            '.*?^\s+plan-create\s+Create a plan.',
            '.*?^See "smaug help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('help')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: smaug plan-create',
            '.*?^Create a plan.',
        ]
        stdout, stderr = self.shell('help plan-create')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_help_no_options(self):
        required = [
            '.*?^usage: smaug',
            '.*?^\s+plan-create\s+Create a plan',
            '.*?^See "smaug help COMMAND" for help on a specific command',
        ]
        stdout, stderr = self.shell('')
        for r in required:
            self.assertThat((stdout + stderr),
                            matchers.MatchesRegex(r, re.DOTALL | re.MULTILINE))

    def test_no_username(self):
        required = ('You must provide a username via either --os-username or '
                    'env[OS_USERNAME] or a token via --os-auth-token or '
                    'env[OS_AUTH_TOKEN]',)
        self.make_env(exclude='OS_USERNAME')
        try:
            self.shell('plan-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_name(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_TENANT_NAME')
        try:
            self.shell('plan-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_tenant_id(self):
        required = self._msg_no_tenant_project
        self.make_env(exclude='OS_TENANT_ID', fake_env=FAKE_ENV2)
        try:
            self.shell('plan-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_no_auth_url(self):
        required = ('You must provide an auth url'
                    ' via either --os-auth-url or via env[OS_AUTH_URL]',)
        self.make_env(exclude='OS_AUTH_URL')
        try:
            self.shell('plan-list')
        except exceptions.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')
