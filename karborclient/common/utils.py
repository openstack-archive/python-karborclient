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

from __future__ import print_function

import os
import sys

import six
import uuid

from oslo_serialization import jsonutils
from oslo_utils import encodeutils

import prettytable

from karborclient.common.apiclient import exceptions


# Decorator for cli-args
def arg(*args, **kwargs):
    def _decorator(func):
        # Because of the sematics of decorator composition if we just append
        # to the options list positional options will appear to be backwards.
        func.__dict__.setdefault('arguments', []).insert(0, (args, kwargs))
        return func
    return _decorator


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v)
        if value:
            return value
    return kwargs.get('default', '')


def _print(pt, order):
    if sys.version_info >= (3, 0):
        print(pt.get_string(sortby=order))
    else:
        print(encodeutils.safe_encode(pt.get_string(sortby=order)))


def print_list(objs, fields, exclude_unavailable=False, formatters=None,
               sortby_index=0):
    '''Prints a list of objects.

    @param objs: Objects to print
    @param fields: Fields on each object to be printed
    @param exclude_unavailable: Boolean to decide if unavailable fields are
                                removed
    @param formatters: Custom field formatters
    @param sortby_index: Results sorted against the key in the fields list at
                         this index; if None then the object order is not
                         altered
    '''
    formatters = formatters or {}
    mixed_case_fields = ['serverId']
    removed_fields = []
    rows = []

    for o in objs:
        row = []
        for field in fields:
            if field in removed_fields:
                continue
            if field in formatters:
                row.append(formatters[field](o))
            else:
                if field in mixed_case_fields:
                    field_name = field.replace(' ', '_')
                else:
                    field_name = field.lower().replace(' ', '_')
                if type(o) == dict and field in o:
                    data = o[field]
                else:
                    if not hasattr(o, field_name) and exclude_unavailable:
                        removed_fields.append(field)
                        continue
                    else:
                        data = getattr(o, field_name, '')
                if data is None:
                    data = '-'
                if isinstance(data, six.string_types) and "\r" in data:
                    data = data.replace("\r", " ")
                row.append(data)
        rows.append(row)

    for f in removed_fields:
        fields.remove(f)

    pt = prettytable.PrettyTable((f for f in fields), caching=False)
    pt.align = 'l'
    for row in rows:
        pt.add_row(row)

    if sortby_index is None:
        order_by = None
    else:
        order_by = fields[sortby_index]
    _print(pt, order_by)


def print_dict(d, property="Property", dict_format_list=None,
               json_format_list=None):
    pt = prettytable.PrettyTable([property, 'Value'], caching=False)
    pt.align = 'l'
    for r in d.items():
        r = list(r)
        if isinstance(r[1], six.string_types) and "\r" in r[1]:
            r[1] = r[1].replace("\r", " ")
        if dict_format_list is not None and r[0] in dict_format_list:
            r[1] = dict_prettyprint(r[1])
        if json_format_list is not None and r[0] in json_format_list:
            r[1] = json_prettyprint(r[1])
        pt.add_row(r)
    _print(pt, property)


def dict_prettyprint(val):
    """dict pretty print formatter.

    :param val: dict.
    :return: formatted json string.
    """
    return jsonutils.dumps(val, indent=2, sort_keys=True)


def json_prettyprint(val):
    """json pretty print formatter.

    :param val: json string.
    :return: formatted json string.
    """
    return val and jsonutils.dumps(jsonutils.loads(val),
                                   indent=2, sort_keys=True)


def find_resource(manager, name_or_id, *args, **kwargs):
    """Helper for the _find_* methods."""
    # first try to get entity as integer id
    try:
        if isinstance(name_or_id, int) or name_or_id.isdigit():
            return manager.get(int(name_or_id), *args, **kwargs)
    except exceptions.NotFound:
        pass

    # now try to get entity as uuid
    try:
        uuid.UUID(str(name_or_id))
        return manager.get(name_or_id, *args, **kwargs)
    except (ValueError, exceptions.NotFound):
        pass

    # finally try to find entity by name
    try:
        return manager.find(name=name_or_id)
    except exceptions.NotFound:
        msg = "No %s with a name or ID of '%s' exists." % \
              (manager.resource_class.__name__.lower(), name_or_id)
        raise exceptions.CommandError(msg)
