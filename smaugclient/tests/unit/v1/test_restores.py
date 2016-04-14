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
mock_request_return = ({}, {'restore': {}})


class RestoresTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_restores_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.restores.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/restores?limit=2&marker=1234', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_restores_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.restores.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/restores?'
            'sort_dir=asc&sort_key=id', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_plans_with_invalid_sort_key(self, mock_request):
        self.assertRaises(ValueError,
                          cs.restores.list, sort_key='invalid', sort_dir='asc')

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_restore(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.restores.create('586cc6ce-e286-40bd-b2b5-dd32694d9944',
                           '2220f8b1-975d-4621-a872-fa9afb43cb6c',
                           '192.168.1.2:35357/v2.0',
                           '{"username": "admin"}')
        mock_request.assert_called_with(
            'POST',
            '/restores',
            data={
                'restore':
                {
                    'checkpoint_id': '2220f8b1-975d-4621-a872-fa9afb43cb6c',
                    'parameters': '{"username": "admin"}',
                    'provider_id': '586cc6ce-e286-40bd-b2b5-dd32694d9944',
                    'restore_target': '192.168.1.2:35357/v2.0'
                }}, headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_restore(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.restores.get('1')
        mock_request.assert_called_with(
            'GET',
            '/restores/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_restore_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.restores.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/restores/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
