from basetest import BaseTest

from katello.client.server import ServerRequestError

from mangonel.common import queued_work
from mangonel.common import wait_for_task

class TestStress(BaseTest):

    def test_stress_128_1(self):
        "Creates a new organization with environment and register a system."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environmemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org, 'Dev'))

        env2 = self.env_api.create(org, 'Testing', 'Dev')
        self.logger.debug("Created environmemt %s" % env2['name'])
        self.assertEqual(env2, self.env_api.environment_by_name(org, 'Testing'))

        env3 = self.env_api.create(org, 'Release', 'Testing')
        self.logger.debug("Created environmemt %s" % env3['name'])
        self.assertEqual(env3, self.env_api.environment_by_name(org, 'Release'))

        prv = self.prv_api.create(org, 'Provider1')
        self.logger.debug("Created custom provider Provider1")
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        prd = self.prd_api.create(prv, 'Product1')
        self.logger.debug("Created product Product1")
        self.assertEqual(prd['id'], self.prd_api.product(org, prd['id'])['id'])

        repo = self.repo_api.create(org, prd, 'http://hhovsepy.fedorapeople.org/fakerepos/zoo4/', 'Repo1')
        self.logger.debug("Created repositiry Repo1")
        self.assertEqual(repo, self.repo_api.repository(repo['id']))

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

        system_time = time.time()
        pools = self.org_api.pools(org['label'])

        all_systems = queued_work(self.sys_api.create, org, env1, 128, 2)
        for sys1 in all_systems:
            self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])

            for pool in pools:
                self.sys_api.subscribe(sys1['uuid'], pool['id'])
                self.logger.debug("Subscribe system to pool %s" % pool['id'])

        total_system_time = time.time() - system_time
        print "Total time spent for systems: %f" % total_system_time
        print "Mean time: %f" % (total_system_time / 128)
