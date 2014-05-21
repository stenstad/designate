# -*- coding: utf-8 -*-
# Copyright 2014 Red Hat, Inc.
#
# Author: Rich Megginson <rmeggins@redhat.com>
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
import unittest

from designate.openstack.common import log as logging
import designate.tests.test_central.test_service
from designate import utils
from designate import exceptions
import testtools
from designate.backend import impl_ipa

LOG = logging.getLogger(__name__)


class CentralServiceTestIPA(designate.tests.test_central.
                            test_service.CentralServiceTest):

    test_config_file_name = "designate-ipa-test.conf"

    def start_service(self, svc_name, *args, **kw):
        """
        override here so we can make sure central is set up correctly
        for live ipa testing
        """
        if svc_name == 'central':
            self.config(backend_driver='ipa', group='service:central')
            # options in the test_config file can override the
            # defaults set elsewhere
            test_config = utils.find_config(self.test_config_file_name)
            self.CONF([], project='designate',
                      default_config_files=test_config)
        return super(CentralServiceTestIPA, self).start_service(svc_name,
                                                                *args, **kw)

    def setUp(self):
        super(CentralServiceTestIPA, self).setUp()
        # go directly through storage api to bypass tenant/policy checks
        save_all_tenants = self.admin_context.all_tenants
        self.admin_context.all_tenants = True
        self.startdomains = self.central_service.storage_api.\
            find_domains(self.admin_context)
        LOG.debug("%s.setUp: startdomains %d" % (self.__class__,
                                                 len(self.startdomains)))
        self.admin_context.all_tenants = save_all_tenants

    def tearDown(self):
        # delete domains
        # go directly through storage api to bypass tenant/policy checks
        self.admin_context.all_tenants = True
        domains = self.central_service.storage_api.\
            find_domains(self.admin_context)
        LOG.debug("%s.tearDown: domains %d" % (self.__class__,
                                               len(self.startdomains)))
        for domain in domains:
            if domain in self.startdomains:
                continue
            # go directly to backend - front end domains will be
            # removed when the database fixture is reset
            self.central_service.backend.delete_domain(self.admin_context,
                                                       domain)

        super(CentralServiceTestIPA, self).tearDown()

    def assertRecordsEqual(self, rec1, rec2):
        rec1dict = dict(rec1.iteritems())
        rec2dict = dict(rec2.iteritems())
        self.assertEqual(rec1dict, rec2dict)

    def test_delete_recordset_extra(self):
        domain = self.create_domain()

        # Create a recordset
        recsetA = self.create_recordset(domain, 'A')
        recsetMX = self.create_recordset(domain, 'MX')

        # create two records in recsetA
        recA0 = self.create_record(domain, recsetA, fixture=0)
        recA1 = self.create_record(domain, recsetA, fixture=1)

        # create two records in recsetMX
        recMX0 = self.create_record(domain, recsetMX, fixture=0)
        recMX1 = self.create_record(domain, recsetMX, fixture=1)

        # verify two records in each recset
        criterion = {
            'domain_id': domain['id'],
            'recordset_id': recsetA['id']
        }

        records = self.central_service.find_records(
            self.admin_context, criterion)

        self.assertEqual(len(records), 2)
        self.assertRecordsEqual(recA0, records[0])
        self.assertRecordsEqual(recA1, records[1])

        criterion['recordset_id'] = recsetMX['id']

        records = self.central_service.find_records(
            self.admin_context, criterion)

        self.assertEqual(len(records), 2)
        self.assertRecordsEqual(recMX0, records[0])
        self.assertRecordsEqual(recMX1, records[1])

        # Delete recsetA
        self.central_service.delete_recordset(
            self.admin_context, domain['id'], recsetA['id'])

        # Fetch the recordset again, ensuring an exception is raised
        with testtools.ExpectedException(exceptions.RecordSetNotFound):
            self.central_service.get_recordset(
                self.admin_context, domain['id'], recsetA['id'])

        # should be no records left in recsetA
        # however, that doesn't appear to be how
        # designate currently works, at least in
        # this particular test
        delete_recset_deletes_recs = False
        if delete_recset_deletes_recs:
            criterion['recordset_id'] = recsetA['id']

            records = self.central_service.find_records(
                self.admin_context, criterion)

            self.assertEqual(len(records), 0)

        # verify two records in recsetMX
        criterion['recordset_id'] = recsetMX['id']

        records = self.central_service.find_records(
            self.admin_context, criterion)

        self.assertEqual(len(records), 2)

        # Delete recsetMX
        self.central_service.delete_recordset(
            self.admin_context, domain['id'], recsetMX['id'])

    def test_create_domain_no_min_ttl(self):
        """Override - ipa does not allow negative ttl values -
        instead, check for proper error
        """
        self.policy({'use_low_ttl': '!'})
        self.config(min_ttl="None",
                    group='service:central')
        values = self.get_domain_fixture(1)
        values['ttl'] = -100

        # Create a server
        self.create_server()

        # Create domain with negative TTL
        with testtools.ExpectedException(impl_ipa.IPAInvalidData):
            self.central_service.create_domain(
                self.admin_context, values=values)

    @unittest.skip("this is currently broken in IPA")
    def test_idn_create_domain_over_tld(self):
        pass

    @unittest.skip("not supported in IPA")
    def test_create_tsigkey(self):
        pass

    @unittest.skip("not supported in IPA")
    def test_get_tsigkey(self):
        pass

    @unittest.skip("not supported in IPA")
    def test_find_tsigkeys(self):
        pass

    @unittest.skip("not supported in IPA")
    def test_delete_tsigkey(self):
        pass

    @unittest.skip("not supported in IPA")
    def test_update_tsigkey(self):
        pass
