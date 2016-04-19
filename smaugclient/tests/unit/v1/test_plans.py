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

import mock

from smaugclient.tests.unit import base
from smaugclient.tests.unit.v1 import fakes

cs = fakes.FakeClient()
mock_request_return = ({}, {'plan': {'name': 'fake_name'}})


class PlansTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_plans_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/plans?limit=2&marker=1234'.format(
                project_id=fakes.PROJECT_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_plans_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/plans?'
            'sort_dir=asc&sort_key=id'.format(
                project_id=fakes.PROJECT_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_plans_with_invalid_sort_key(self, mock_request):
        self.assertRaises(ValueError,
                          cs.plans.list, sort_key='invalid', sort_dir='asc')

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_plan(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.create('Plan name', 'provider_id', '', "")
        mock_request.assert_called_with(
            'POST',
            '/plans',
            data={
                'plan': {'provider_id': 'provider_id',
                         'name': 'Plan name',
                         'resources': '',
                         'parameters': ''}},
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.raw_request')
    def test_delete_plan(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.delete('1')
        mock_request.assert_called_with(
            'DELETE',
            '/plans/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_update(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.update('1', {'name': 'Test name.'})
        mock_request.assert_called_with(
            'PUT',
            '/plans/1',
            data={'plan': {'name': 'Test name.'}}, headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_plan(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.get('1')
        mock_request.assert_called_with(
            'GET',
            '/plans/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_plan_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.plans.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/plans/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
