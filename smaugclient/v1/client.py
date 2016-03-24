#    Copyright (c) 2013 Mirantis, Inc.
#
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

from smaugclient.common import http
from smaugclient.v1 import checkpoints
from smaugclient.v1 import plans
from smaugclient.v1 import protectables
from smaugclient.v1 import providers
from smaugclient.v1 import restores
from smaugclient.v1 import scheduled_operations
from smaugclient.v1 import triggers


class Client(object):
    """Client for the Smaug v1 API.

    :param string endpoint: A user-supplied endpoint URL for the service.
    :param string token: Token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Smaug v1 API."""
        self.http_client = http._construct_http_client(*args, **kwargs)
        self.plans = plans.PlanManager(self.http_client)
        self.restores = restores.RestoreManager(self.http_client)
        self.protectables = protectables.ProtectableManager(self.http_client)
        self.providers = providers.ProviderManager(self.http_client)
        self.checkpoints = checkpoints.CheckpointManager(self.http_client)
        self.triggers = triggers.TriggerManager(self.http_client)
        self.scheduled_operations = \
            scheduled_operations.ScheduledOperationManager(self.http_client)
