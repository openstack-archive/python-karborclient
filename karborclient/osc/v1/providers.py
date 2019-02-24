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

"""Data protection V1 provider action implementations"""

import functools
from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

from karborclient.i18n import _


class ListProviders(command.Lister):
    _description = _("List providers.")

    log = logging.getLogger(__name__ + ".ListProviders")

    def get_parser(self, prog_name):
        parser = super(ListProviders, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filters results by a name. Default=None.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Filters results by a description. Default=None.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<provider>',
            help=_('The last provider ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-providers>',
            help=_('Maximum number of providers to display'),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc) "
                   "(default: name:asc), multiple keys and directions can be "
                   "specified separated by comma"),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection

        search_opts = {
            'name': parsed_args.name,
            'description': parsed_args.description,
        }

        data = data_protection_client.providers.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Name', 'Description']

        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class ShowProvider(command.ShowOne):
    _description = "Shows provider details"

    def get_parser(self, prog_name):
        parser = super(ShowProvider, self).get_parser(prog_name)
        parser.add_argument(
            'provider',
            metavar="<provider>",
            help=_('The UUID of the provider.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        provider = osc_utils.find_resource(client.providers,
                                           parsed_args.provider)
        json_dumps = functools.partial(jsonutils.dumps,
                                       indent=2, sort_keys=True)
        provider._info.pop("links", None)
        if 'extended_info_schema' in provider._info:
            provider._info['extended_info_schema'] = json_dumps(
                provider._info['extended_info_schema'])
        return zip(*sorted(provider._info.items()))
