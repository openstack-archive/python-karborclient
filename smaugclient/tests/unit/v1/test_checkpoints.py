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
mock_request_return = ({}, {'checkpoint': {}})

FAKE_PROVIDER_ID = "2220f8b1-975d-4621-a872-fa9afb43cb6c"
FAKE_PLAN_ID = "3330f8b1-975d-4621-a872-fa9afb43cb6c"


class CheckpointsTest(base.TestCaseShell):

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_checkpoints(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.list(provider_id=FAKE_PROVIDER_ID)
        mock_request.assert_called_with(
            'GET',
            '/providers/{provider_id}/checkpoints'.format(
                provider_id=FAKE_PROVIDER_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_get_checkpoint(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.get(FAKE_PROVIDER_ID, '1')
        mock_request.assert_called_with(
            'GET',
            '/providers/{provider_id}/checkpoints/1'.format(
                provider_id=FAKE_PROVIDER_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.raw_request')
    def test_delete_checkpoint(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.delete(FAKE_PROVIDER_ID, '1')
        mock_request.assert_called_with(
            'DELETE',
            '/providers/{provider_id}/checkpoints/1'.format(
                provider_id=FAKE_PROVIDER_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_checkpoints_with_marker_limit(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.list(provider_id=FAKE_PROVIDER_ID,
                            marker=1234, limit=2)
        mock_request.assert_called_with(
            'GET',
            '/providers/{provider_id}/'
            'checkpoints?limit=2&marker=1234'.format(
                provider_id=FAKE_PROVIDER_ID), headers={})

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_list_checkpoints_with_sort_key_dir(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.list(provider_id=FAKE_PROVIDER_ID,
                            sort_key='id', sort_dir='asc')
        mock_request.assert_called_with(
            'GET',
            '/providers/{provider_id}/'
            'checkpoints?sort_dir=asc&sort_key=id'.format(
                provider_id=FAKE_PROVIDER_ID), headers={})

    def test_list_checkpoints_with_invalid_sort_key(self):
        self.assertRaises(ValueError,
                          cs.checkpoints.list, FAKE_PROVIDER_ID,
                          sort_key='invalid', sort_dir='asc')

    @mock.patch('smaugclient.common.http.HTTPClient.json_request')
    def test_create_checkpoint(self, mock_request):
        mock_request.return_value = mock_request_return
        cs.checkpoints.create(FAKE_PROVIDER_ID, FAKE_PLAN_ID)
        mock_request.assert_called_with(
            'POST',
            '/providers/{provider_id}/'
            'checkpoints'.format(
                provider_id=FAKE_PROVIDER_ID),
            data={
                'checkpoint': {'plan_id': FAKE_PLAN_ID}},
            headers={})
