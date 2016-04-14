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
mock_request_return = ({}, {'scheduled_operation': {'name': 'fake_name'}})


class ScheduledOperationsTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_scheduled_operations_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/scheduled_operations?limit=2&marker=1234', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list__scheduled_operations_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/scheduled_operations?'
            'sort_dir=asc&sort_key=id', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_scheduled_operations_with_invalid_sort_key(self,
                                                             mock_request):
        self.assertRaises(ValueError,
                          cs.scheduled_operations.list, sort_key='invalid',
                          sort_dir='asc')

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_scheduled_operation(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.create(
            'name', 'operation_type',
            'efc6a88b-9096-4bb6-8634-cda182a6e12a',
            'operation_definition')
        mock_request.assert_called_with(
            'POST',
            '/scheduled_operations',
            data={
                'scheduled_operation': {
                    'name': 'name',
                    'operation_type': 'operation_type',
                    'trigger_id': 'efc6a88b-9096-4bb6-8634-cda182a6e12a',
                    'operation_definition': 'operation_definition'}},
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.raw_request')
    def test_delete_scheduled_operation(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.delete('1')
        mock_request.assert_called_with(
            'DELETE',
            '/scheduled_operations/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_scheduled_operation(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.get('1')
        mock_request.assert_called_with(
            'GET',
            '/scheduled_operations/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_scheduled_operation_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.scheduled_operations.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/scheduled_operations/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
