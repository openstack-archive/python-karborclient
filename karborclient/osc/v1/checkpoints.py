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

"""Data protection V1 checkpoint action implementations"""

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.common.apiclient import exceptions
from karborclient.i18n import _
from karborclient import utils


class ListCheckpoints(command.Lister):
    _description = _("List checkpoints.")

    log = logging.getLogger(__name__ + ".ListCheckpoints")

    def get_parser(self, prog_name):
        parser = super(ListCheckpoints, self).get_parser(prog_name)
        parser.add_argument(
            'provider_id',
            metavar='<provider_id>',
            help=_('ID of provider.'),
        )
        parser.add_argument(
            '--plan_id',
            metavar='<plan_id>',
            default=None,
            help=_('Filters results by a plan ID. Default=None.'),
        )
        parser.add_argument(
            '--start_date',
            type=str,
            metavar='<start_date>',
            default=None,
            help=_('Filters results by a start date("Y-m-d"). Default=None.'),
        )
        parser.add_argument(
            '--end_date',
            type=str,
            metavar='<end_date>',
            default=None,
            help=_('Filters results by a end date("Y-m-d"). Default=None.'),
        )
        parser.add_argument(
            '--project_id',
            metavar='<project_id>',
            default=None,
            help=_('Filters results by a project ID. Default=None.'),
        )
        parser.add_argument(
            '--marker',
            metavar='<checkpoint>',
            help=_('The last checkpoint ID of the previous page.'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar='<num-checkpoints>',
            help=_('Maximum number of checkpoints to display.'),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default=None,
            help=_("Sort output by selected keys and directions(asc or desc), "
                   "multiple keys and directions can be "
                   "specified separated by comma"),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection

        search_opts = {
            'plan_id': parsed_args.plan_id,
            'start_date': parsed_args.start_date,
            'end_date': parsed_args.end_date,
            'project_id': parsed_args.project_id,
        }

        data = data_protection_client.checkpoints.list(
            provider_id=parsed_args.provider_id, search_opts=search_opts,
            marker=parsed_args.marker, limit=parsed_args.limit,
            sort=parsed_args.sort)

        column_headers = ['Id', 'Project id', 'Status', 'Protection plan',
                          'Metadata', 'Created at']

        def plan_formatter(plan):
            return "Name: %s\nId: %s" % (plan['name'],
                                         plan['id'])
        formatters = {"Protection plan": plan_formatter}
        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers, formatters=formatters
                ) for s in data))


class ShowCheckpoint(command.ShowOne):
    _description = "Shows checkpoint details"

    def get_parser(self, prog_name):
        parser = super(ShowCheckpoint, self).get_parser(prog_name)
        parser.add_argument(
            'provider_id',
            metavar="<provider_id>",
            help=_('Id of provider.')
        )
        parser.add_argument(
            'checkpoint_id',
            metavar="<checkpoint_id>",
            help=_('Id of checkpoint.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        checkpoint = client.checkpoints.get(parsed_args.provider_id,
                                            parsed_args.checkpoint_id)
        checkpoint._info.pop("links", None)
        return zip(*sorted(checkpoint._info.items()))


class CreateCheckpoint(command.ShowOne):
    _description = "Creates a checkpoint"

    def get_parser(self, prog_name):
        parser = super(CreateCheckpoint, self).get_parser(prog_name)
        parser.add_argument(
            'provider_id',
            metavar='<provider_id>',
            help=_('ID of provider.')
        )
        parser.add_argument(
            'plan_id',
            metavar='<plan_id>',
            help=_('ID of plan.')
        )
        parser.add_argument(
            '--extra_info',
            type=str,
            nargs='*',
            metavar='<key=value>',
            default=None,
            help=_('The extra info of a checkpoint.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        checkpoint_extra_info = None
        if parsed_args.extra_info is not None:
            checkpoint_extra_info = utils.extract_extra_info(parsed_args)
        checkpoint = client.checkpoints.create(parsed_args.provider_id,
                                               parsed_args.plan_id,
                                               checkpoint_extra_info)
        checkpoint._info.pop("links", None)
        return zip(*sorted(checkpoint._info.items()))


class DeleteCheckpoint(command.Command):
    _description = "Delete checkpoint"

    log = logging.getLogger(__name__ + ".DeleteCheckpoint")

    def get_parser(self, prog_name):
        parser = super(DeleteCheckpoint, self).get_parser(prog_name)
        parser.add_argument(
            'provider_id',
            metavar='<provider_id>',
            help=_('Id of provider.')
        )
        parser.add_argument(
            'checkpoint',
            metavar='<checkpoint>',
            nargs="+",
            help=_('Id of checkpoint.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        failure_count = 0
        for checkpoint_id in parsed_args.checkpoint:
            try:
                client.checkpoints.delete(parsed_args.provider_id,
                                          checkpoint_id)
            except exceptions.NotFound:
                failure_count += 1
                self.log.error(
                    "Failed to delete '{0}'; checkpoint not found".
                    format(checkpoint_id))
        if failure_count == len(parsed_args.checkpoint):
            raise exceptions.CommandError(
                "Unable to find and delete any of the "
                "specified checkpoint.")
