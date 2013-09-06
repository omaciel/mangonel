from common import *

import sys

try:
    from katello.client.api.user_role import UserRoleAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class UserRole(UserRoleAPI):

    def __init__(self):
        super(UserRole, self).__init__()

    def create(self, name=None, description=None):

        if name is None:
            name = "role-%s" % generate_name(4)

        if description is None:
            description = "Generated automatically"

        role = super(UserRole, self).create(name, description)

        logger.debug("Created user role '%s'" % role['name'])

        return role
