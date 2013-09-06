from common import *

import sys

try:
    from katello.client.api.permission import PermissionAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class Permission(PermissionAPI):

    def __init__(self):
        super(Permission, self).__init__()

    def create(self, roleId, type_in, verbs, tagIds, name=None, description=None,
               orgId=None, all_tags=False, all_verbs=False):

        if name is None:
            name = "role-%s" % generate_name(4)

        if description is None:
            description = "Generated automatically"

        permission = super(permission, self).create(roleId, name, description, type_in, verbs, tagIds,
                                                    orgId, all_tags, all_verbs)

        logger.debug("Created user permission '%s'" % permission['name'])

        return permission
