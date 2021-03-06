# COPYRIGHT 2015 Hewlett-Packard Development Company, L.P.
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

from oslo_log import log as logging

from designate.api.v2.controllers import rest
from designate.api.admin.controllers.extensions import import_
from designate.api.admin.controllers.extensions import export

LOG = logging.getLogger(__name__)


class ZonesController(rest.RestController):

    @staticmethod
    def get_path():
        return '.zones'

    def __init__(self):
        # Import is a keyword - so we have to do a setattr instead
        setattr(self, 'import', import_.ImportController())
        super(ZonesController, self).__init__()

    # We cannot do an assignment as import is a keyword. it is done as part of
    # the __init__() above
    #
    # import = import_.CountsController()
    export = export.ExportController()
