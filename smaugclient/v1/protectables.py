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


class Protectable(base.Resource):
    def __repr__(self):
        return "<Protectable %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class Instances(base.Resource):
    def __repr__(self):
        return "<Instances %s>" % self._info

    def data(self, **kwargs):
        return self.manager.data(self, **kwargs)


class ProtectableManager(base.ManagerWithFind):
    resource_class = Protectable

    def get(self, protectable_type, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/protectables/{protectable_type}".format(
            protectable_type=protectable_type)
        return self._get(url, response_key="protectable_type", headers=headers)

    def list(self):
        url = "/protectables"
        protectables = self._list(url, 'protectable_type', return_raw=True)

        protectables_list = []
        for protectable in protectables:
            protectable_dict = {}
            protectable_dict['protectable_type'] = protectable
            protectables_list.append(Protectable(self, protectable_dict))
        return protectables_list

    def list_instances(self, protectable_type, search_opts=None, marker=None,
                       limit=None, sort_key=None, sort_dir=None, sort=None):
        """Lists all instances.

        :param protectable_type:
        :param search_opts: Search options to filter out instances.
        :param marker: Begin returning volumes that appear later in the
                       instances list.
        :param limit: Maximum number of instances to return.
        :param sort_key: Key to be sorted; deprecated in kilo
        :param sort_dir: Sort direction, should be 'desc' or 'asc'; deprecated
                         in kilo
        :param sort: Sort information
        :rtype: list of :class:`Instances`
        """

        url = self._build_instances_list_url(
            protectable_type,
            search_opts=search_opts, marker=marker,
            limit=limit, sort_key=sort_key,
            sort_dir=sort_dir, sort=sort)
        return self._list(url, response_key='instances', obj_class=Instances)

    def get_instance(self, type, id, session_id=None):
        if session_id:
            headers = {'X-Configuration-Session': session_id}
        else:
            headers = {}
        url = "/protectables/{protectable_type}/" \
              "instances/{protectable_id}".format(protectable_type=type,
                                                  protectable_id=id)
        return self._get(url, response_key="instance", headers=headers)

    def _build_instances_list_url(self, protectable_type,
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

        return ("/protectables/%(protectable_type)s"
                "/instances%(query_string)s" %
                {"protectable_type": protectable_type,
                 "query_string": query_string})
