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

from mangonel.activationkey import ActivationKey
from mangonel.changeset import Changeset
from mangonel.contentview import ContentView
from mangonel.contentviewdefinition import ContentViewDefinition
from mangonel.environment import Environment
from mangonel.organization import Organization
from mangonel.permission import Permission
from mangonel.product import Product
from mangonel.provider import Provider
from mangonel.repository import Repository
from mangonel.system import System
from mangonel.systemgroup import SystemGroup
from mangonel.server import Server
from mangonel.user import User
from mangonel.user_role import UserRole

def runIf(project):
    "Decorator to skip tests based on server mode"
    mode = os.getenv('PROJECT').replace('/', '')

    if mode == 'sam':
        mode = 'headpin'

    if project == mode:
        return lambda func: func
    return unittest.skip("%s specific test." % project)

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

        self.verbosity = int(os.getenv('VERBOSITY', 2))
        self.ssh_key = os.getenv('SSH_KEY', os.path.expanduser('~/.ssh/id_rsa'))
        self.root = os.getenv('ROOT', 'root')

        logging.config.fileConfig("logging.conf")

        self.logger = logging.getLogger("mangonel")
        self.logger.setLevel(self.verbosity * 10)

        self.ak_api = ActivationKey()
        self.chs_api = Changeset()
        self.cv_api = ContentView()
        self.cvd_api = ContentViewDefinition()
        self.env_api = Environment()
        self.org_api = Organization()
        self.perm_api = Permission()
        self.prd_api = Product()
        self.prv_api = Provider()
        self.repo_api = Repository()
        self.sys_api = System()
        self.sys_grp_api = SystemGroup()
        self.user_api = User()
        self.role_api = UserRole()

        self.start_time = time.time()

    def tearDown(self):
        self.server = None

        self.ellapsed_time = time.time() - self.start_time
        self.logger.info("Test ellapsed time: %s" % self.ellapsed_time)

    def uptime(self):
        "Checks the system's load average"

        try:
            import paramiko
        except ImportError, e:
            return "Please install paramiko to obtain the system load average."

        # Make paramiko less chatty
        logging.getLogger("paramiko").setLevel(logging.ERROR)

        if self.root is None or self.ssh_key is None:
            return "Please provide the required credentials to ssh to the remote server."

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(self.host, username=self.root, key_filename=self.ssh_key)
        except IOError, e:
            return "Make sure that your ssh key exists and is accessible."

        stdin, stdout, stderr = ssh_client.exec_command('uptime')

        return stdout.readlines()[0]
