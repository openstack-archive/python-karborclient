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

"""Data protection V1 os-services action implementations"""

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from karborclient.i18n import _


class ListServices(command.Lister):
    _description = _("List services.")

    log = logging.getLogger(__name__ + ".ListServices")

    def get_parser(self, prog_name):
        parser = super(ListServices, self).get_parser(prog_name)
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_('Filter results by host'),
        )
        parser.add_argument(
            '--binary',
            metavar='<binary>',
            help=_('Filter results by binary'),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        data_protection_client = self.app.client_manager.data_protection
        data = data_protection_client.services.list(
            host=parsed_args.host,
            binary=parsed_args.binary
        )

        column_headers = ["Id", "Binary", "Host", "Status", "State",
                          "Updated_at", "Disabled Reason"]
        return (column_headers,
                (osc_utils.get_item_properties(
                    s, column_headers
                ) for s in data))


class EnableService(command.ShowOne):
    _description = _('Enable service')

    def get_parser(self, prog_name):
        parser = super(EnableService, self).get_parser(prog_name)
        parser.add_argument(
            'service_id',
            metavar='<service_id>',
            help=_('The ID of the service.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        service = client.services.enable(parsed_args.service_id)
        return zip(*sorted(service._info.items()))


class DisableService(command.ShowOne):
    _description = _('Disable service')

    def get_parser(self, prog_name):
        parser = super(DisableService, self).get_parser(prog_name)
        parser.add_argument(
            'service_id',
            metavar='<service_id>',
            help=_('The ID of the service.'),
        )
        parser.add_argument(
            '--reason',
            metavar='<reason>',
            help=_('Reason for disabling the service.')
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        if parsed_args.reason:
            service = client.services.disable_log_reason(
                parsed_args.service_id, parsed_args.reason)
        else:
            service = client.services.disable(parsed_args.service_id)
        return zip(*sorted(service._info.items()))
