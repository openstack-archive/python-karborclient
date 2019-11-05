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

from karborclient.tests.unit import base
from karborclient.tests.unit.v1 import fakes

cs = fakes.FakeClient()
mock_request_return = ({}, {'operation_log': {}})


class OperationLogsTest(base.TestCaseShell):

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_operation_logs(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.list()
        mock_request.assert_called_with(
            'GET',
            '/operation_logs', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_operation_logs_with_all_tenants(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.list(search_opts={'all_tenants': 1})
        mock_request.assert_called_with(
            'GET',
            '/operation_logs?all_tenants=1', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_operation_logs_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/operation_logs?limit=2&marker=1234', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_operation_logs_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/operation_logs?'
            'sort_dir=asc&sort_key=id', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_operation_logs_with_invalid_sort_key(self, mock_request):
        self.assertRaises(ValueError,
                          cs.operation_logs.list,
                          sort_key='invalid', sort_dir='asc')

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_operation_log(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.get('1')
        mock_request.assert_called_with(
            'GET',
            '/operation_logs/1',
            headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_operation_log_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.operation_logs.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/operation_logs/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
