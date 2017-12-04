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

"""Data protection V1 quotas action implementations"""

from osc_lib.command import command


def quota_set_pretty_show(quotas):
    """Convert quotas object to dict and display."""

    new_quotas = []
    for quota_k, quota_v in sorted(quotas.to_dict().items()):
        if isinstance(quota_v, dict):
            quota_v = '\n'.join(
                ['%s = %s' % (k, v) for k, v in sorted(quota_v.items())])
        new_quotas.append((quota_k, quota_v))

    return new_quotas


class ShowQuotas(command.ShowOne):
    _description = "Shows Quotas"

    def get_parser(self, prog_name):
        parser = super(ShowQuotas, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            default=None,
            help='ID of tenant to list the quotas for.')
        parser.add_argument(
            '--detail',
            action='store_true',
            help='Optional flag to indicate whether to show quota in detail. '
                 'Default false.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        project_id = parsed_args.tenant or client.http_client.get_project_id()
        kwargs = {
            "project_id": project_id,
            "detail": parsed_args.detail,
        }
        result = client.quotas.get(**kwargs)
        quotas = quota_set_pretty_show(result)
        return zip(*sorted(quotas))


class ShowDefaultQuotas(command.ShowOne):
    _description = "Shows default Quotas"

    def get_parser(self, prog_name):
        parser = super(ShowDefaultQuotas, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            default=None,
            help='ID of tenant to list the quotas for.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        project_id = parsed_args.tenant or client.http_client.get_project_id()

        result = client.quotas.defaults(project_id)
        quotas = quota_set_pretty_show(result)

        return zip(*sorted(quotas))


class UpdateQuotas(command.ShowOne):
    _description = "Updates Quotas"

    def get_parser(self, prog_name):
        parser = super(UpdateQuotas, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='ID of tenant to set the quotas for.')
        parser.add_argument(
            '--plans',
            metavar='<plans>',
            type=int,
            default=None,
            help='New value for the "plans" quota.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        project_id = parsed_args.tenant
        data = {
            "plans": parsed_args.plans,
        }
        result = client.quotas.update(project_id, data)
        quotas = quota_set_pretty_show(result)

        return zip(*sorted(quotas))
