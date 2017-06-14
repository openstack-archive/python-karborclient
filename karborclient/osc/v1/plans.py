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

"""Data protection V1 plan action implementations"""

from osc_lib.command import command
from osc_lib import utils
from oslo_log import log as logging

from karborclient.i18n import _


class ListPlans(command.Lister):
    _description = _("List plans.")

    log = logging.getLogger(__name__ + ".ListPlans")

    def get_parser(self, prog_name):
        parser = super(ListPlans, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Filter results by plan name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Filter results by plan description'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter results by status'),
        )
        parser.add_argument(
            '--marker',
            metavar='<plan>',
            help=_('The last plan ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-plans>',
            help=_('Maximum number of plans to display'),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc) "
                   "(default: name:asc), multiple keys and directions can be "
                   "specified separated by comma"),
        )
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            help=_('Filter results by a tenant(admin only)')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection
        all_projects = bool(parsed_args.tenant) or parsed_args.all_projects

        search_opts = {
            'all_tenants': all_projects,
            'project_id': parsed_args.tenant,
            'name': parsed_args.name,
            'description': parsed_args.description,
            'status': parsed_args.status,
        }

        data = data_protection_client.plans.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Name', 'Description', 'Provider id', 'Status']

        return (column_headers,
                (utils.get_item_properties(
                    s, column_headers
                ) for s in data))
