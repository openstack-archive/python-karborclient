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

"""
Base utilities to build API operation managers and objects on top of.
"""

import abc
import copy

import six
from six.moves.urllib import parse

from smaugclient.common import http
from smaugclient.openstack.common.apiclient import exceptions

SORT_DIR_VALUES = ('asc', 'desc')
SORT_KEY_VALUES = ('id', 'status', 'name', 'created_at')
SORT_KEY_MAPPINGS = {}


def getid(obj):
    """Abstracts the common pattern of allowing both an object or

    an object's ID (UUID) as a parameter when dealing with relationships.
    """

    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(object):
    """Managers interact with a particular type of API (servers, flavors,

    images, etc.) and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, api):
        self.api = api
        if isinstance(self.api, http.SessionClient):
            self.project_id = self.api.get_project_id()
        else:
            self.project_id = self.api.project_id

    def _list(self, url, response_key=None, obj_class=None,
              data=None, headers=None, return_raw=False,):

        if headers is None:
            headers = {}
        resp, body = self.api.json_request('GET', url, headers=headers)

        if obj_class is None:
            obj_class = self.resource_class

        if response_key:
            if response_key not in body:
                body[response_key] = []
            data = body[response_key]
        else:
            data = body
        if return_raw:
            return data
        return [obj_class(self, res, loaded=True) for res in data if res]

    def _delete(self, url, headers=None):
        if headers is None:
            headers = {}
        self.api.raw_request('DELETE', url, headers=headers)

    def _update(self, url, data, response_key=None, headers=None):
        if headers is None:
            headers = {}
        resp, body = self.api.json_request('PUT', url, data=data,
                                           headers=headers)
        # PUT requests may not return a body
        if body:
            if response_key:
                return self.resource_class(self, body[response_key])
            return self.resource_class(self, body)

    def _create(self, url, data=None, response_key=None,
                return_raw=False, headers=None):
        if headers is None:
            headers = {}
        if data:
            resp, body = self.api.json_request('POST', url,
                                               data=data, headers=headers)
        else:
            resp, body = self.api.json_request('POST', url, headers=headers)
        if return_raw:
            if response_key:
                return body[response_key]
            return body
        if response_key:
            return self.resource_class(self, body[response_key])
        return self.resource_class(self, body)

    def _get(self, url, response_key=None, return_raw=False, headers=None):
        if headers is None:
            headers = {}
        resp, body = self.api.json_request('GET', url, headers=headers)
        if return_raw:
            if response_key:
                return body[response_key]
            return body
        if response_key:
            return self.resource_class(self, body[response_key])
        return self.resource_class(self, body)

    def _build_list_url(self, resource_type, detailed=False,
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

        detail = ""
        if detailed:
            detail = "/detail"

        return ("/%(resource_type)s%(detail)s"
                "%(query_string)s" %
                {"resource_type": resource_type, "detail": detail,
                 "query_string": query_string})

    def _format_sort_param(self, sort):
        '''Formats the sort information into the sort query string parameter.

        The input sort information can be any of the following:
        - Comma-separated string in the form of <key[:dir]>
        - List of strings in the form of <key[:dir]>
        - List of either string keys, or tuples of (key, dir)

        For example, the following import sort values are valid:
        - 'key1:dir1,key2,key3:dir3'
        - ['key1:dir1', 'key2', 'key3:dir3']
        - [('key1', 'dir1'), 'key2', ('key3', dir3')]

        :param sort: Input sort information
        :returns: Formatted query string parameter or None
        :raise ValueError: If an invalid sort direction or invalid sort key is
                           given
        '''
        if not sort:
            return None

        if isinstance(sort, six.string_types):
            # Convert the string into a list for consistent validation
            sort = [s for s in sort.split(',') if s]

        sort_array = []
        for sort_item in sort:
            if isinstance(sort_item, tuple):
                sort_key = sort_item[0]
                sort_dir = sort_item[1]
            else:
                sort_key, _sep, sort_dir = sort_item.partition(':')
            sort_key = sort_key.strip()
            if sort_key in SORT_KEY_VALUES:
                sort_key = SORT_KEY_MAPPINGS.get(sort_key, sort_key)
            else:
                raise ValueError('sort_key must be one of the following: %s.'
                                 % ', '.join(SORT_KEY_VALUES))
            if sort_dir:
                sort_dir = sort_dir.strip()
                if sort_dir not in SORT_DIR_VALUES:
                    msg = ('sort_dir must be one of the following: %s.'
                           % ', '.join(SORT_DIR_VALUES))
                    raise ValueError(msg)
                sort_array.append('%s:%s' % (sort_key, sort_dir))
            else:
                sort_array.append(sort_key)
        return ','.join(sort_array)

    def _format_sort_key_param(self, sort_key):
        if sort_key in SORT_KEY_VALUES:
            return SORT_KEY_MAPPINGS.get(sort_key, sort_key)

        msg = ('sort_key must be one of the following: %s.' %
               ', '.join(SORT_KEY_VALUES))
        raise ValueError(msg)

    def _format_sort_dir_param(self, sort_dir):
        if sort_dir in SORT_DIR_VALUES:
            return sort_dir

        msg = ('sort_dir must be one of the following: %s.'
               % ', '.join(SORT_DIR_VALUES))
        raise ValueError(msg)


@six.add_metaclass(abc.ABCMeta)
class ManagerWithFind(Manager):
    """Manager with additional `find()`/`findall()` methods."""

    @abc.abstractmethod
    def list(self):
        pass

    def find(self, **kwargs):
        """Find a single item with attributes matching ``**kwargs``.

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        rl = self.findall(**kwargs)
        num = len(rl)

        if num == 0:
            msg = "No %s matching %s." % (self.resource_class.__name__, kwargs)
            raise exceptions.NotFound(msg)
        elif num > 1:
            raise exceptions.NoUniqueMatch
        else:
            return self.get(rl[0].id)

    def findall(self, **kwargs):
        """Find all items with attributes matching ``**kwargs``.

        This isn't very efficient: it loads the entire list then filters on
        the Python side.
        """
        found = []
        searches = kwargs.items()

        for obj in self.list():
            try:
                if all(getattr(obj, attr) == value
                       for (attr, value) in searches):
                    found.append(obj)
            except AttributeError:
                continue

        return found


class Resource(object):
    """A resource represents a particular instance of an object (tenant, user,

    etc). This is pretty much just a bag for attributes.

    :param manager: Manager object
    :param info: dictionary representing resource attributes
    :param loaded: prevent lazy-loading if set to True
    """
    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def _add_details(self, info):
        for k, v in info.items():
            setattr(self, k, v)

    def __setstate__(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def __getattr__(self, k):
        if k not in self.__dict__:
            # NOTE(bcwaldon): disallow lazy-loading if already loaded once
            if not self.is_loaded():
                self.get()
                return self.__getattr__(k)
            raise AttributeError(k)
        else:
            return self.__dict__[k]

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                          k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self.set_loaded(True)
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.id)
        if new:
            self._add_details(new._info)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._info == other._info

    def is_loaded(self):
        return self._loaded

    def set_loaded(self, val):
        self._loaded = val

    def to_dict(self):
        return copy.deepcopy(self._info)
