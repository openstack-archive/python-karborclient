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

"""Data protection V1 quota classes action implementations"""

from osc_lib.command import command


def quota_class_set_pretty_show(quota_classes):
    """Convert quotas class object to dict and display."""

    new_quota_classes = []
    for quota_k, quota_v in sorted(quota_classes.to_dict().items()):
        if isinstance(quota_v, dict):
            quota_v = '\n'.join(
                ['%s = %s' % (k, v) for k, v in sorted(quota_v.items())])
        new_quota_classes.append((quota_k, quota_v))

    return new_quota_classes


class ShowQuotaClasses(command.ShowOne):
    _description = "Shows Quota classes."

    def get_parser(self, prog_name):
        parser = super(ShowQuotaClasses, self).get_parser(prog_name)
        parser.add_argument(
            'class_name',
            metavar='<class_name>',
            help='Name of quota class to list the quotas for.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        result = client.quota_classes.get(parsed_args.class_name)
        quota_classes = quota_class_set_pretty_show(result)
        return zip(*sorted(quota_classes))


class UpdateQuotaClasses(command.ShowOne):
    _description = "Update the quotas for a quota class (Admin only)."

    def get_parser(self, prog_name):
        parser = super(UpdateQuotaClasses, self).get_parser(prog_name)
        parser.add_argument(
            'class_name',
            metavar='<class_name>',
            help='Name of quota class to set the quotas for.')
        parser.add_argument(
            '--plans',
            metavar='<plans>',
            type=int,
            default=None,
            help='New value for the "plans" quota.')
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.data_protection
        class_name = parsed_args.class_name
        data = {
            "plans": parsed_args.plans,
        }
        result = client.quota_classes.update(class_name, data)
        quota_classes = quota_class_set_pretty_show(result)

        return zip(*sorted(quota_classes))
