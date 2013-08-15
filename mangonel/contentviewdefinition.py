from common import *

import datetime
import json
import sys
import time

try:
    from katello.client.api.task_status import TaskStatusAPI
    from katello.client.api.content_view_definition import ContentViewDefinitionAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class ContentViewDefinition(ContentViewDefinitionAPI):
    task_api = TaskStatusAPI()

    def __init__(self):
        super(ContentViewDefinition, self).__init__()

    def create(self, org, name=None, label=None, description=None, composite=False):

        if name is None:
            name = generate_name(8)

        if label is None:
            label = "label-%s" % name.lower()

        if description is None:
            description = "Created on %s" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        return super(ContentViewDefinition, self).create(org['label'], name, label, description, composite)

    def content_view_definition(self, org, cvdId):
        return super(ContentViewDefinition, self).show(org['label'], cvdId)


    def content_view_definitions_by_org(self, org):
        return super(ContentViewDefinition, self).content_view_definitions_by_org(org['label'])

    def publish(self, org, cvdId, name=None, label=None, description=None):

        if name is None:
            name = generate_name(8)


        if label is None:
            label = "label-%s" % name.lower()

        if description is None:
            description = "Published on %s" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        ptask = super(ContentViewDefinition, self).publish(org['label'], cvdId, name, label, description)

        task = self.task_api.status(ptask['uuid'])

        for i in range(MAX_ATTEMPTS):
            task = self.task_api.status(ptask['uuid'])

            if task['state'] == 'finished' or task['state'] == 'error':
                break

            logger.info("Publishing content view description %s" % name)
            logger.debug(task['state'])
            time.sleep(REQUEST_DELAY)
        else:
            task = None

        return task

    def clone(self, org, cvdId, name=None, label=None, description=None):

        if name is None:
            name = generate_name(8)


        if label is None:
            label = "label-%s" % name.lower()

        if description is None:
            description = "Cloned on %s" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        return super(ContentViewDefinition, self).clone(org['label'], cvdId, name, label, description)

    def update_products(self, org, cvdId, prd):
        return super(ContentViewDefinition, self).update_products(org['label'], cvdId, [prd['id']])

    def products(self, org, cvdId):
        return super(ContentViewDefinition, self).products(org['label'], cvdId)
