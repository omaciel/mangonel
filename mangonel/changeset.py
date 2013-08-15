from common import *

import datetime
import json
import sys
import time

try:
    from katello.client.api.task_status import TaskStatusAPI
    from katello.client.api.changeset import ChangesetAPI
except ImportError, e:
    print "Please install Katello CLI package."
    sys.exit(-1)


class Changeset(ChangesetAPI):
    task_api = TaskStatusAPI()

    def __init__(self):
        super(Changeset, self).__init__()

    def create(self, org, env, name=None, type_in='promotion', description=None):

        if name is None:
            name = generate_name(8)

        if description is None:
            description = "Promoted on %s" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        return super(Changeset, self).create(org['label'], env['id'], name, type_in, description)

    def changeset_by_name(self, org, env, name):
        return super(Changeset, self).changeset_by_name(org['label'], env['id'], name)

    def add_content(self, chsId, content, contentType='content_views'):
        return super(Changeset, self).add_content(chsId, contentType, {'content_view_id' : content['id'] })

    def apply(self, chsId):
        applyTask = super(Changeset, self).apply(chsId)

        task = self.task_api.status(applyTask['uuid'])

        for i in range(MAX_ATTEMPTS):
            task = self.task_api.status(applyTask['uuid'])

            if task['state'] == 'finished' or task['state'] == 'error':
                break

            logger.info("Promoting content...")
            logger.debug(task['state'])
            time.sleep(REQUEST_DELAY)
        else:
            task = None

        return task


