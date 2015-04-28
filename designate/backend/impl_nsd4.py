# Copyright 2015 Zetta.IO.
#
# Author: Dag Stenstad <dag@stenstad.net>
#
# Based on work from: Ron Rickard <rrickard@ebay.com>
#                     Artom Lifshitz <artom.lifshitz@enovance.com>
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

import random, socket, ssl, eventlet

from oslo_log import log as logging

from designate import exceptions
from designate import utils
from designate.backend import base


LOG = logging.getLogger(__name__)
DEFAULT_MASTER_PORT = 5354


class NSD4Backend(base.Backend):
    __plugin_name__ = 'nsd4'
    NSDCT_VERSION = 'NSDCT1'

    def __init__(self, target):
        super(NSD4Backend, self).__init__(target)

        self.host = self.options.get('host', '127.0.0.1')
        self.port = int(self.options.get('port', 8952))
        self.certfile = self.options.get('certfile', '/etc/nsd/nsd_control.pem')
        self.keyfile = self.options.get('keyfile', '/etc/nsd/nsd_control.key')
        self.pattern = self.options.get('pattern', 'slave')

    def create_domain(self, context, domain):
        LOG.debug('Create Domain')
        masters = []
        for master in self.masters:
            host = master['host']
            port = master['port']
            masters.append('%s port %s' % (host, port))

        # Ensure different MiniDNS instances are targetted for AXFRs
        random.shuffle(masters)

        command = [
            'addzone',
            '%s %s' % (domain['name'], self._pattern),
        ]

        try:
            self._execute_nsd4(command)
        except exceptions.Backend as e:
            # If create fails because the domain exists, don't reraise
            if "already exists" not in str(e.message):
                raise

    def delete_domain(self, context, domain):
        LOG.debug('Delete Domain')
        command = [
            'delzone',
            '%s' % domain['name'],
        ]

        try:
            self._execute_nsd4(command)
        except exceptions.Backend as e:
            # If domain is already deleted, don't reraise
            if "not found" not in str(e.message):
                raise

    def _command(self):
        sock = eventlet.wrap_ssl(eventlet.connect((self.host, self.port)),
                                 keyfile=self._keyfile,
                                 certfile=self._certfile)
        stream = sock.makefile()
        stream.write('%s %s\n' % (self.NSDCT_VERSION, command))
        stream.flush()
        result = stream.read()
        stream.close()
        sock.close()
        return result.rstrip()

    def _execute_nsd4(self, command):
        try:
            LOG.debug('Executing NSD4 control call: %s' % " ".join(command))
            result = self._command(command)
            nsd4_call.extend(nsd4_op)
            _
            LOG.debug('Executing NSD4 control call: %s' % " ".join(rndc_call))
            utils.execute(*nsd4_call)
        except (ssl.SSLError, socket.error) as e:
            LOG.debug('NSD4 control call failure: %s' % e)
            raise exceptions.Backend(e)

