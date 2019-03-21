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

"""Data protection V1 protectables action implementations"""

import functools
from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

from karborclient.i18n import _
from karborclient import utils


class ListProtectables(command.Lister):
    _description = _("List protectable types.")

    log = logging.getLogger(__name__ + ".ListProtectables")

    def get_parser(self, prog_name):
        parser = super(ListProtectables, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection

        data = data_protection_client.protectables.list()

        column_headers = ['Protectable type']

        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class ShowProtectable(command.ShowOne):
    _description = "Shows protectable type details"

    def get_parser(self, prog_name):
        parser = super(ShowProtectable, self).get_parser(prog_name)
        parser.add_argument(
            'protectable_type',
            metavar="<protectable_type>",
            help=_('Protectable type.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        protectable = osc_utils.find_resource(client.protectables,
                                              parsed_args.protectable_type)

        protectable._info.pop("links", None)
        if 'dependent_types' in protectable._info:
            protectable._info['dependent_types'] = "\n".join(
                protectable._info['dependent_types'])
        return zip(*sorted(protectable._info.items()))


class ListProtectableInstances(command.Lister):
    _description = _("List protectable instances.")

    log = logging.getLogger(__name__ + ".ListProtectableInstances")

    def get_parser(self, prog_name):
        parser = super(ListProtectableInstances, self).get_parser(prog_name)
        parser.add_argument(
            'protectable_type',
            metavar="<protectable_type>",
            help=_('Type of protectable.')
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            default=None,
            help=_('Filters results by protectable type. Default=None.')
        )
        parser.add_argument(
            '--marker',
            metavar="<protectable_instance>",
            default=None,
            help=_('The last protectable instance ID of the previous page.')
        )
        parser.add_argument(
            '--limit',
            metavar="<num-protectable_instances>",
            default=None,
            help=_('Maximum number of protectable instances to display.')
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc), "
                   "multiple keys and directions can be "
                   "specified separated by comma"),
        )
        parser.add_argument(
            '--parameters',
            type=str,
            nargs='*',
            metavar="<key=value>",
            default=None,
            help=_('List instances by parameters key and value pair. '
                   'Default=None.')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection

        search_opts = {
            'type': parsed_args.type,
            'parameters': (utils.extract_instances_parameters(parsed_args)
                           if parsed_args.parameters else None),
        }

        data = data_protection_client.protectables.list_instances(
            parsed_args.protectable_type, search_opts=search_opts,
            marker=parsed_args.marker, limit=parsed_args.limit,
            sort=parsed_args.sort)

        column_headers = ['Id', 'Type', 'Name', 'Dependent resources',
                          'Extra info']

        json_dumps = functools.partial(jsonutils.dumps,
                                       indent=2, sort_keys=True)
        formatters = {
            "Extra info": json_dumps,
            "Dependent resources": json_dumps,
        }
        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers, formatters=formatters,
                ) for s in data))


class ShowProtectableInstance(command.ShowOne):
    _description = "Shows protectable instance details"

    def get_parser(self, prog_name):
        parser = super(ShowProtectableInstance, self).get_parser(prog_name)
        parser.add_argument(
            'protectable_type',
            metavar="<protectable_type>",
            help=_('Protectable type.')
        )
        parser.add_argument(
            'protectable_id',
            metavar="<protectable_id>",
            help=_('Protectable instance id.')
        )
        parser.add_argument(
            '--parameters',
            type=str,
            nargs='*',
            metavar="<key=value>",
            default=None,
            help=_('Show a instance by parameters key and value pair. '
                   'Default=None.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection

        search_opts = {
            'parameters': (utils.extract_instances_parameters(parsed_args)
                           if parsed_args.parameters else None),
        }

        instance = client.protectables.get_instance(
            parsed_args.protectable_type,
            parsed_args.protectable_id,
            search_opts=search_opts)

        json_dumps = functools.partial(jsonutils.dumps,
                                       indent=2, sort_keys=True)
        instance._info.pop("links", None)
        for key in ('extra_info', 'dependent_resources'):
            if key not in instance._info:
                continue
            instance._info[key] = json_dumps(instance._info[key])

        return zip(*sorted(instance._info.items()))
