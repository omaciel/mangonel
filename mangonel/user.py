from common import *

import sys

try:
    from katello.client.api.user import UserAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class User(UserAPI):

    def __init__(self):
        super(User, self).__init__()

    def create(self, name=None, pw=None, email=None, disabled=False, default_env=None, default_loc=None):

        if name is None:
            name = "user-%s" % generate_name(4)

        if pw is None:
            pw = generate_name(8)

        if email is None:
            email = "%s@example.com" % name

        user = super(User, self).create(name, pw, email, disabled, default_env, default_loc)

        logger.debug("Created system user '%s'" % user['username'])

        return user

    def update(self, user_id, pw=None, email=None, disabled=None, default_environment=None, default_locale=None):

        return super(User, self).update(user_id, pw, email, disabled, default_environment, default_locale)
