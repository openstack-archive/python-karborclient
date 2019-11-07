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
mock_request_return = ({}, {'quota': {'plans': 50}})


class QuotasTest(base.TestCaseShell):

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_quota_update(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.update(fakes.PROJECT_ID, {'plans': 50})
        mock_request.assert_called_with(
            'PUT',
            '/quotas/{project_id}'.format(project_id=fakes.PROJECT_ID),
            data={'quota': {'plans': 50}}, headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_quota_update_with_none(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.update(fakes.PROJECT_ID, {'plans': None})
        mock_request.assert_called_with(
            'PUT',
            '/quotas/{project_id}'.format(project_id=fakes.PROJECT_ID),
            data={'quota': {'plans': 50}}, headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_quota(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.get(fakes.PROJECT_ID, detail=False)
        mock_request.assert_called_with(
            'GET',
            '/quotas/{project_id}'.format(project_id=fakes.PROJECT_ID),
            headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_quota_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.get(fakes.PROJECT_ID, False, session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/quotas/{project_id}'.format(project_id=fakes.PROJECT_ID),
            headers={'X-Configuration-Session': 'fake_session_id'})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_quota_with_detail(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.get(fakes.PROJECT_ID, detail=True)
        mock_request.assert_called_with(
            'GET',
            '/quotas/{project_id}/detail'.format(
                project_id=fakes.PROJECT_ID),
            headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_quota_with_default(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.defaults(fakes.PROJECT_ID)
        mock_request.assert_called_with(
            'GET',
            '/quotas/{project_id}/defaults'.format(
                project_id=fakes.PROJECT_ID),
            headers={})

    @mock.patch('karborclient.common.http.HTTPClient.json_request')
    def test_show_quota_default_with_headers(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.quotas.defaults(fakes.PROJECT_ID, session_id='fake_session_id')
        mock_request.assert_called_with(
            'GET',
            '/quotas/{project_id}/defaults'.format(
                project_id=fakes.PROJECT_ID),
            headers={'X-Configuration-Session': 'fake_session_id'})
