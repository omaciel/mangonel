from common import *

import datetime
import json
import sys
import time

try:
    from katello.client.api.repo import RepoAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class Repository():
    api = RepoAPI()

    def create_repository(self, org, prd, url, name=None, label=None, unprotected=True, gpgkey=None, nogpgkey=None):

        if name is None:
            name = generate_name(8)

        if label is None:
            label = "label-%s" % name.lower()

        resp = self.api.create(org['label'], prd['id'], name, label, url, unprotected, gpgkey, nogpgkey)

        repositories = self.api.repos_by_product(org['label'], prd['id'])
        repo = [repo for repo in repositories if repo['name'] == name]

        if repo:
            repo = repo[0]

        return repo


    def delete_repository(self, rId):
        return self.api.delete(rId)


    def repository(self, rId):
        return self.api.repo(rId)


    def repositories_by_product(self, org, prd, includeDisabled=False):
        return self.api.repositories_by_repo(org['label'], prd['id'], includeDisabled)
