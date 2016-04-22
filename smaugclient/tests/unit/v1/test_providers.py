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
mock_request_return = ({}, {'provider': {}})


class ProvidersTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_get_providers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.providers.get('2220f8b1-975d-4621-a872-fa9afb43cb6c')
        mock_request.assert_called_with(
            'GET',
            '/providers/'
            '2220f8b1-975d-4621-a872-fa9afb43cb6c', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_providers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.providers.list()
        mock_request.assert_called_with(
            'GET',
            '/providers', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_providers_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.providers.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/providers?limit=2&marker=1234', headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_providers_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.providers.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/providers?'
            'sort_dir=asc&sort_key=id', headers={})

    def test_list_providers_with_invalid_sort_key(self):
        self.assertRaises(ValueError,
                          cs.providers.list,
                          sort_key='invalid', sort_dir='asc')
