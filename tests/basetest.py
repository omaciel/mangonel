import logging
import logging.config

import os
import sys
import time
import unittest

try:
    from katello.client.server import ServerRequestError
except ImportError, e:
    print "Please install the Katello CLI package."
    sys.exit(-1)

try:
    from nose.plugins.skip import SkipTest
except ImportError, e:
    print "Please install python nose."
    sys.exit(-1)

from mangonel.activationkey import ActivationKey
from mangonel.changeset import Changeset
from mangonel.contentview import ContentView
from mangonel.contentviewdefinition import ContentViewDefinition
from mangonel.environment import Environment
from mangonel.organization import Organization
from mangonel.product import Product
from mangonel.provider import Provider
from mangonel.repository import Repository
from mangonel.system import System
from mangonel.systemgroup import SystemGroup
from mangonel.server import Server
from mangonel.user import User

def katello_only():
    "Decorator to allow skipping Headpin-specific tests."
    if os.getenv('PROJECT') in ['/headpin', '/sam']:
        return SkipTest
    return lambda func: func

def headpin_only():
    "Decorator to allow skipping Headpin-specific tests."
    if os.getenv('PROJECT') in ['/katello']:
        return SkipTest
    return lambda func: func

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.host = os.getenv('KATELLO_HOST')
        self.port = os.getenv('KATELLO_PORT', '443')
        self.project = os.getenv('PROJECT', '/katello')

        # Make sure that PROJECT starts with a leading "/"
        if not self.project.startswith("/"): self.project = "/" + self.project

        self.user = os.getenv('KATELLO_USERNAME', None)
        self.password = os.getenv('KATELLO_PASSWORD', None)

        self.server = Server(host=self.host,
                       project=self.project,
                       username=self.user,
                       password=self.password,
                       port=self.port)

        self.verbosity = int(os.getenv('VERBOSITY', 3))

        logging.config.fileConfig("logging.conf")

        self.logger = logging.getLogger("mangonel")
        self.logger.setLevel(self.verbosity * 10)

        self.ak_api = ActivationKey()
        self.chs_api = Changeset()
        self.cv_api = ContentView()
        self.cvd_api = ContentViewDefinition()
        self.env_api = Environment()
        self.org_api = Organization()
        self.prd_api = Product()
        self.prv_api = Provider()
        self.repo_api = Repository()
        self.sys_api = System()
        self.sys_grp_api = SystemGroup()
        self.user_api = User()

        self.start_time = time.time()

    def tearDown(self):
        self.server = None

        self.ellapsed_time = time.time() - self.start_time
        self.logger.info("Test ellapsed time: %s" % self.ellapsed_time)
