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
mock_request_return = ({}, {'trigger_info': {'name': 'fake_name'}})


class TriggersTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_triggers_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/triggers?limit=2&marker=1234', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_triggers_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/triggers?'
            'sort_dir=asc&sort_key=id', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_triggers_with_invalid_sort_key(self, mock_request):
        self.assertRaises(ValueError,
                          cs.triggers.list, sort_key='invalid', sort_dir='asc')

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_trigger(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.create('name', 'time', 'properties')
        mock_request.assert_called_with(
            'POST',
            '/triggers',
            data={
                'trigger_info': {'name': 'name',
                                 'type': 'time',
                                 'properties': 'properties'}},
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.raw_request')
    def test_delete_trigger(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.delete('1')
        mock_request.assert_called_with(
            'DELETE',
            '/triggers/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_plan(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.get('1')
        mock_request.assert_called_with(
            'GET',
            '/triggers/1',
            headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_show_trigger_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.triggers.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/triggers/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
