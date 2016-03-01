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

from smaugclient.common import utils


@utils.arg('--all-tenants', action='store_true', default=False,
           help='Allows to list plans from all tenants'
                ' (admin only).')
def do_plan_list(mc, args=None):
    """List the plans."""
    pass


def do_plan_create(mc, args):
    """Create a plan."""
    pass
