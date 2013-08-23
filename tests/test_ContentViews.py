from basetest import BaseTest
from basetest import runIf

from katello.client.server import ServerRequestError
from mangonel.common import wait_for_task

@runIf('katello')
class TestContentViews(BaseTest):

    def test_create_content_view_1(self):
        "Creates an empty content view."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environmemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        # Content View Definition
        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")
        self.assertEqual(cvd, self.cvd_api.content_view_definition(org, cvd['id']))

        # Published Content view
        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

    def test_create_content_view_2(self):
        "Creates a new content view with real content."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environmemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        prv = self.prv_api.create(org, 'Provider1')
        self.logger.debug("Created custom provider Provider1")
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        prd = self.prd_api.create(prv, 'Product1')
        self.logger.debug("Created product Product1")
        self.assertEqual(prd['id'], self.prd_api.product(org, prd['id'])['id'])

        repo = self.repo_api.create(org, prd, 'http://hhovsepy.fedorapeople.org/fakerepos/zoo4/', 'Repo1')
        self.logger.debug("Created repositiry Repo1")
        self.assertEqual(repo, self.repo_api.repo(repo['id']))

        # Sync
        task_id = self.prv_api.sync(prv['id'])
        task = wait_for_task(task_id[0]['uuid'])
        self.assertNotEqual(task, None)

        self.assertEqual(self.prv_api.provider(prv['id'])['sync_state'], 'finished')
        self.logger.debug("Finished synchronizing Provider1")

        # Content View Definition
        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")
        self.assertEqual(cvd, self.cvd_api.content_view_definition(org, cvd['id']))
        prods = self.cvd_api.update_products(org, cvd['id'], prd)
        self.logger.debug("Added %s to Content View Definition" % prd['name'])

        # Published Content view
        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

