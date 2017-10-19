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
mock_request_return = ({}, {'verification': {}})


class VerificationsTest(base.TestCaseShell):

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_verifications_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.verifications.list(marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/verifications?limit=2&marker=1234', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_verifications_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.verifications.list(sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/verifications?'
            'sort_dir=asc&sort_key=id', headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_verifications_with_invalid_sort_key(self, mock_request):
        self.assertRaises(ValueError,
                          cs.verifications.list,
                          sort_key='invalid', sort_dir='asc')

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_create_verification(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.verifications.create('586cc6ce-e286-40bd-b2b5-dd32694d9944',
                                '2220f8b1-975d-4621-a872-fa9afb43cb6c',
                                '{}')
        mock_request.assert_called_with(
            'POST',
            '/verifications',
            data={
                'verification':
                {
                    'checkpoint_id': '2220f8b1-975d-4621-a872-fa9afb43cb6c',
                    'parameters': '{}',
                    'provider_id': '586cc6ce-e286-40bd-b2b5-dd32694d9944'
                }}, headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_verification(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.verifications.get('1')
        mock_request.assert_called_with(
            'GET',
            '/verifications/1',
            headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_verification_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.verifications.get('1', session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/verifications/1',
            headers={'X-Configuration-Session': 'fake_session_id'})
