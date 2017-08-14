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

"""Data protection V1 operation_log action implementations"""

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.i18n import _


class ListOperationLogs(command.Lister):
    _description = _("List operation_logs.")

    log = logging.getLogger(__name__ + ".ListOperationLogs")

    def get_parser(self, prog_name):
        parser = super(ListOperationLogs, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter results by status'),
        )
        parser.add_argument(
            '--marker',
            metavar='<operation_log>',
            help=_('The last operation_log ID of the previous page'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-operation_logs>',
            help=_('Maximum number of operation_logs to display'),
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
            '--project',
            metavar='<project>',
            help=_('Filter results by a project(admin only)')
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection
        all_projects = bool(parsed_args.project) or parsed_args.all_projects

        search_opts = {
            'all_tenants': all_projects,
            'project_id': parsed_args.project,
            'status': parsed_args.status,
        }

        data = data_protection_client.operation_logs.list(
            search_opts=search_opts, marker=parsed_args.marker,
            limit=parsed_args.limit, sort=parsed_args.sort)

        column_headers = ['Id', 'Operation Type', 'Checkpoint id',
                          'Plan Id', 'Provider id', 'Restore Id',
                          'Scheduled Operation Id', 'Status',
                          'Started At', 'Ended At', 'Error Info',
                          'Extra Info']

        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class ShowOperationLog(command.ShowOne):
    _description = "Shows operation_log details"

    def get_parser(self, prog_name):
        parser = super(ShowOperationLog, self).get_parser(prog_name)
        parser.add_argument(
            'operation_log',
            metavar="<operation_log>",
            help=_('The UUID of the operation_log.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        operation_log = osc_utils.find_resource(client.operation_logs,
                                                parsed_args.operation_log)

        operation_log._info.pop("links", None)
        return zip(*sorted(operation_log._info.items()))
