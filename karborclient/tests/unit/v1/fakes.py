# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from karborclient.common import http as base_client
from karborclient.tests.unit import base
from karborclient.tests.unit import fakes
from karborclient.v1 import client


REQUEST_ID = 'req-test-request-id'
PROJECT_ID = 'efc6a88b-9096-4bb6-8634-cda182a6e12a'


class FakeClient(fakes.FakeClient, client.Client):

    def __init__(self, *args, **kwargs):
        kwargs = {
            'token': 'token',
            'auth': 'auth_url',
            'service_type': 'service_type',
            'endpoint_type': 'endpoint_type',
            'region_name': 'region_name',
            'project_id': PROJECT_ID,
        }
        client.Client.__init__(self, 'http://endpoint', **kwargs)
        self.client = self.http_client


class FakeHTTPClient(base_client.HTTPClient):

    def __init__(self, endpoint, **kwargs):
        super(FakeHTTPClient, self)
        self.username = 'username'
        self.password = 'password'
        self.auth_url = 'auth_url'
        self.callstack = []
        self.management_url = 'http://10.0.2.15:8776/v1/fake'
        self.osapi_max_limit = 1000
        self.marker = None
        self.project_id = 'project_id'
        self.auth_token = 'auth_token'
        self.region_name = 'region_name'

    def _cs_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert 'body' not in kwargs
        elif method == 'PUT':
            assert 'body' in kwargs

        # Call the method
        args = urlparse.parse_qsl(urlparse.urlparse(url)[4])
        kwargs.update(args)
        url_split = url.rsplit('?', 1)
        munged_url = url_split[0]
        if len(url_split) > 1:
            parameters = url_split[1]
            if 'marker' in parameters:
                self.marker = int(parameters.rsplit('marker=', 1)[1])
            else:
                self.marker = None
        else:
            self.marker = None
        munged_url = munged_url.strip('/').replace('/', '_').replace('.', '_')
        munged_url = munged_url.replace('-', '_')

        callback = "%s_%s" % (method.lower(), munged_url)

        if not hasattr(self, callback):
            raise AssertionError('Called unknown API method: %s %s, '
                                 'expected fakes method name: %s' %
                                 (method, url, callback))

        # Note the call
        self.callstack.append((method, url, kwargs.get('body')))
        status, headers, body = getattr(self, callback)(**kwargs)
        # add fake request-id header
        headers['x-openstack-request-id'] = REQUEST_ID
        r = base.TestResponse({
            "status_code": status,
            "text": body,
            "headers": headers,
        })
        return r, body

    def json_request(self, method, url, **kwargs):
        return self._cs_request(url, method, **kwargs)

    def get_providers_1234_checkpoints(self, **kwargs):
        return 200, {}, {"checkpoints": []}

    def get_plans(self, **kwargs):
        return 200, {}, {"plans": []}

    def get_operation_logs(self, **kwargs):
        return 200, {}, {"operation_logs": []}

    def get_restores(self, **kwargs):
        return 200, {}, {"restores": []}

    def get_scheduled_operations(self, **kwargs):
        return 200, {}, {"operations": []}

    def get_triggers(self, **kwargs):
        return 200, {}, {"triggers": []}

    def get_verifications(self, **kwargs):
        return 200, {}, {"verifications": []}
