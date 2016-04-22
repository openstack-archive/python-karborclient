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

from six.moves.urllib import parse

from smaugclient.common import base


class Checkpoint(base.Resource):
    def __repr__(self):
        return "<Checkpoint %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class CheckpointManager(base.ManagerWithFind):
    resource_class = Checkpoint

    def create(self, provider_id, plan_id):
        body = {'checkpoint': {'plan_id': plan_id}}
        url = "/providers/{provider_id}/" \
              "checkpoints" .format(provider_id=provider_id)
        return self._create(url, body, 'checkpoint', return_raw=True)

    def delete(self, provider_id, checkpoint_id):
        path = '/providers/{provider_id}/checkpoints/' \
               '{checkpoint_id}'.format(provider_id=provider_id,
                                        checkpoint_id=checkpoint_id)
        return self._delete(path)

    def get(self, provider_id, checkpoint_id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = '/providers/{provider_id}/checkpoints/' \
            '{checkpoint_id}'.format(provider_id=provider_id,
                                     checkpoint_id=checkpoint_id)
        return self._get(url, response_key="checkpoint", headers=headers)

    def list(self, provider_id=None, search_opts=None, marker=None,
             limit=None, sort_key=None, sort_dir=None, sort=None):
        """Lists all checkpoints.

        :param provider_id:
        :param search_opts: Search options to filter out checkpoints.
        :param marker: Begin returning checkpoints that appear later in the
                       checkpoints list.
        :param limit: Maximum number of checkpoints to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`checkpoint`
        """

        url = self._build_checkpoints_list_url(
            provider_id,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, 'checkpoints')

    def _build_checkpoints_list_url(self, provider_id,
                                    search_opts=None, marker=None, limit=None,
                                    sort_key=None, sort_dir=None, sort=None):

        if search_opts is None:
            search_opts = {}

        query_params = {}
        for key, val in search_opts.items():
            if val:
                query_params[key] = val

        if marker:
            query_params['marker'] = marker

        if limit:
            query_params['limit'] = limit

        if sort:
            query_params['sort'] = self._format_sort_param(sort)
        else:
            # sort_key and sort_dir deprecated in kilo, prefer sort
            if sort_key:
                query_params['sort_key'] = self._format_sort_key_param(
                    sort_key)

            if sort_dir:
                query_params['sort_dir'] = self._format_sort_dir_param(
                    sort_dir)

        # Transform the dict to a sequence of two-element tuples in fixed
        # order, then the encoded string will be consistent in Python 2&3.
        query_string = ""
        if query_params:
            params = sorted(query_params.items(), key=lambda x: x[0])
            query_string = "?%s" % parse.urlencode(params)

        return ("/providers/%(provider_id)s"
                "/checkpoints%(query_string)s" %
                {"provider_id": provider_id,
                 "query_string": query_string})
