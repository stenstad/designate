# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import eventlet

eventlet.monkey_patch(os=False)

import os
import socket

from oslo.config import cfg
from oslo import messaging


cfg.CONF.import_opt('default_log_levels', 'designate.openstack.common.log')

cfg.CONF.register_opts([
    cfg.StrOpt('host', default=socket.gethostname(),
               help='Name of this node'),
    cfg.StrOpt('pybasedir',
               default=os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    '../')),
               help='Directory where the nova python module is installed'),
    cfg.StrOpt('state-path', default='/var/lib/designate',
               help='Top-level directory for maintaining designate\'s state'),

    cfg.StrOpt('central-topic', default='central', help='Central Topic'),
    cfg.StrOpt('mdns-topic', default='mdns', help='mDNS Topic'),
    cfg.StrOpt('pool-manager-topic', default='pool_manager',
               help='Pool Manager Topic'),

    # Default TTL
    cfg.IntOpt('default-ttl', default=3600),

    # Default SOA Values
    cfg.IntOpt('default-soa-refresh', default=3600),
    cfg.IntOpt('default-soa-retry', default=600),
    cfg.IntOpt('default-soa-expire', default=86400),
    cfg.IntOpt('default-soa-minimum', default=3600),
])

# Set some Oslo Log defaults
cfg.CONF.set_default('default_log_levels',
                     ['amqplib=WARN',
                      'amqp=WARN',
                      'sqlalchemy=WARN',
                      'boto=WARN',
                      'suds=INFO',
                      'keystone=INFO',
                      'eventlet.wsgi.server=WARN',
                      'stevedore=WARN',
                      'keystonemiddleware.auth_token=INFO'])

# Set some Oslo RPC defaults
messaging.set_transport_defaults('designate')
