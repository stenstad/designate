# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
from oslo.config import cfg

from designate.tests.test_api.test_v2 import ApiV2TestCase


class ApiV2LimitsTest(ApiV2TestCase):
    def test_get_limits(self):
        response = self.client.get('/limits/')

        self.assertEqual(200, response.status_int)
        self.assertEqual('application/json', response.content_type)

        self.assertIn('max_zones', response.json)
        self.assertIn('max_zone_records', response.json)
        self.assertIn('max_zone_recordsets',
                      response.json)
        self.assertIn('max_recordset_records',
                      response.json)

        absolutelimits = response.json

        self.assertEqual(cfg.CONF.quota_domains, absolutelimits['max_zones'])
        self.assertEqual(cfg.CONF.quota_domain_records,
                         absolutelimits['max_zone_recordsets'])
