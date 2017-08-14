#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import logging

from osc_lib import utils

LOG = logging.getLogger(__name__)

DEFAULT_DATA_PROTECTION_API_VERSION = '1'
API_VERSION_OPTION = 'os_data_protection_api_version'
API_NAME = 'data_protection'
API_VERSIONS = {
    '1': 'karborclient.v1.client.Client',
}


def make_client(instance):
    """Returns a data protection service client"""
    data_protection_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating data protection client: %s',
              data_protection_client)
    client = data_protection_client(
        auth=instance.auth,
        session=instance.session,
        service_type="data-protect"
    )

    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-data-protection-api-version',
        metavar='<data-protection-api-version>',
        default=utils.env(
            'OS_DATA_PROTECTION_API_VERSION',
            default=DEFAULT_DATA_PROTECTION_API_VERSION),
        help='Data protection API version, default=' +
             DEFAULT_DATA_PROTECTION_API_VERSION +
             ' (Env: OS_DATA_PROTECTION_API_VERSION)')
    return parser
