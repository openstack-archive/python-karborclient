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
mock_request_return = ({}, {'service': {}})


class ServicesTest(base.TestCaseShell):

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_services(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.services.list()
        mock_request.assert_called_with(
            'GET',
            '/os-services',
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_services_with_host(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.services.list(host='fake_host')
        mock_request.assert_called_with(
            'GET',
            '/os-services?host=fake_host',
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_services_with_binary(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.services.list(binary='fake_binary')
        mock_request.assert_called_with(
            'GET',
            '/os-services?binary=fake_binary',
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_list_services_with_host_and_binary(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.services.list(host='fake_host', binary='fake_binary')
        mock_request.assert_called_with(
            'GET',
            '/os-services?binary=fake_binary&host=fake_host',
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_enable_service(self, mock_request):
        mock_request.return_value = mock_request_return
        body = {
            'status': 'enabled'
        }
        cs.services.enable('1')
        mock_request.assert_called_with(
            'PUT',
            '/os-services/1',
            data=body,
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_disable_service(self, mock_request):
        mock_request.return_value = mock_request_return
        body = {
            'status': 'disabled'
        }
        cs.services.disable('1')
        mock_request.assert_called_with(
            'PUT',
            '/os-services/1',
            data=body,
            headers={}
        )

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_disable_service_with_reason(self, mock_request):
        mock_request.return_value = mock_request_return
        body = {
            'status': 'disabled',
            'disabled_reason': 'fake_reason'
        }
        cs.services.disable_log_reason('1', 'fake_reason')
        mock_request.assert_called_with(
            'PUT',
            '/os-services/1',
            data=body,
            headers={}
        )
