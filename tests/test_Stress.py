import time

from basetest import BaseTest
from basetest import headpin_only
from basetest import katello_only

from katello.client.server import ServerRequestError

from mangonel.common import queued_work
from mangonel.common import wait_for_task

JOB_SAMPLES = [128, 256, 512, 1024, 2048, 4096]
JOB_THREADS = [1, 2, 4, 8, 16]


class TestStress(BaseTest):

    def _generate_content(self):
        "Creates a new organization with environment and real content."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environmemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        env2 = self.env_api.create(org, 'Testing', 'Dev')
        self.logger.debug("Created environmemt %s" % env2['name'])
        self.assertEqual(env2, self.env_api.environment_by_name(org['label'], 'Testing'))

        env3 = self.env_api.create(org, 'Release', 'Testing')
        self.logger.debug("Created environmemt %s" % env3['name'])
        self.assertEqual(env3, self.env_api.environment_by_name(org['label'], 'Release'))

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
        prods = self.cvd_api.update_products(org, cvd['id'], prd)
        self.logger.debug("Added %s to Content View Definition" % prd['name'])

        # Published Content view
        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

        # Changeset
        chs = self.chs_api.create(org, env1, 'Promote01')
        self.logger.debug("Created promotion changeset Promote01")
        self.chs_api.add_content(chs['id'], pcvd)
        self.logger.debug("Added %s to changeset" % pcvd['name'])
        self.chs_api.apply(chs['id'])

        return (org, env1)

    def test_organizations(self):

        for outter in JOB_SAMPLES:
            for inner in JOB_THREADS:

                start_time = time.time()

                all_organizations = queued_work(self.org_api.create, outter, inner)

                end_time = time.time()

                for org in all_organizations:
                    self.assertTrue(self.org_api.organization(org['name']))

                total_system_time = end_time - start_time
                self.logger.info("Total time spent for %s organizations using %s threads: %f" % (outter, inner, total_system_time))
                self.logger.info("Mean time: %f" % (total_system_time / outter))

    @katello_only()
    def test_providers(self):

        for outter in JOB_SAMPLES:
            for inner in JOB_THREADS:

                org = self.org_api.create()
                self.logger.info("Created organization %s" % org['name'])
                self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

                env = self.env_api.environment_by_name(org['label'], 'Library')

                start_time = time.time()

                all_providers = queued_work(self.prv_api.create, outter, inner, org)

                end_time = time.time()

                for prv in all_providers:
                    self.assertEqual(prv, self.prv_api.provider(prv['id']))

                total_system_time = end_time - start_time
                self.logger.info("Total time spent for %s providers using %s threads: %f" % (outter, inner, total_system_time))
                self.logger.info("Mean time: %f" % (total_system_time / outter))

    @katello_only()
    def test_systems_1(self):

        for outter in JOB_SAMPLES:
            for inner in JOB_THREADS:

                (org, env) = self._generate_content()

                start_time = time.time()

                all_systems = queued_work(self.sys_api.create, outter, inner, org, env)

                end_time = time.time()

                for sys1 in all_systems:
                    self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])

                    pools = self.org_api.pools(org['label'])

                    for pool in pools:
                        self.sys_api.subscribe(sys1['uuid'], pool['id'])
                        self.logger.debug("Subscribe system to pool %s" % pool['id'])

                total_system_time = end_time - start_time
                self.logger.info("Total time spent for %s systems using %s threads: %f" % (outter, inner, total_system_time))
                self.logger.info("Mean time: %f" % (total_system_time / outter))

    @headpin_only()
    def test_systems_2(self):

        for outter in JOB_SAMPLES:
            for inner in JOB_THREADS:

                org = self.org_api.create()
                env = self.env_api.environment_by_name(org['label'], 'Library')

                start_time = time.time()

                all_systems = queued_work(self.sys_api.create, outter, inner, org, env)

                end_time = time.time()

                for sys1 in all_systems:
                    self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])

                #TODO: Add support for adding a manifest and
                #subscribing systems to a pool

                total_system_time = end_time - start_time
                self.logger.info("Total time spent for %s systems using %s threads: %f" % (outter, inner, total_system_time))
                self.logger.info("Mean time: %f" % (total_system_time / outter))
