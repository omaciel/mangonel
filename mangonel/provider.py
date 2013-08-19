from common import *

import datetime
import json
import sys
import time

try:
    from katello.client.api.provider import ProviderAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class Provider(ProviderAPI):

    def __init__(self):
        super(Provider, self).__init__()

    def create(self, org, name=None, description='Built by API', ptype='Custom', url=None):

        if name is None:
            name = generate_name(8)

        return super(Provider, self).create(name, org['label'], description, ptype, url)

    def delete(self, name):
        return super(Provider, self).delete(name)

    def provider(self, pId):
        return super(Provider, self).provider(pId)

    def providers_by_org(self, org):
        return super(Provider, self).providers_by_org(org['label'])
