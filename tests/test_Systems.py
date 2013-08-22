from basetest import BaseTest

from katello.client.server import ServerRequestError

from mangonel.common import queued_work

class TestSystems(BaseTest):

    def test_create_1(self):
        "Creates a new organization with environment and register a system."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        sys1 = self.sys_api.create(org, library)
        self.logger.debug("Created system %s" % sys1['uuid'])
        self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])

    def test_create_2(self):
        "Cannot register a system to an environment that has no content views."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        self.assertRaises(ServerRequestError, lambda: self.sys_api.create(org, env))

    def test_create_3(self):
        "Register a system to an environment that has one content view."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")

        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        sys1 = self.sys_api.create(org, library, view_id=pcvd['id'])
        self.assertEqual(pcvd['definition'], sys1['content_view']['definition'])

    def test_create_4(self):
        "Register a system to an environment that has one content views."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")

        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')

        # Changeset
        chs = self.chs_api.create(org, env, 'Promote01')
        self.logger.debug("Created promotion changeset Promote01")
        self.chs_api.add_content(chs['id'], pcvd)
        self.logger.debug("Added %s to changeset" % pcvd['name'])
        self.chs_api.apply(chs['id'])

        sys1 = self.sys_api.create(org, env, view_id=pcvd['id'])
        self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])
        self.assertEqual(pcvd['definition'], sys1['content_view']['definition'])

    def test_stress_systems_1(self):
        "Creates a new organization with environment and registers 12 systems 2 at a time."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        env = self.env_api.create(org, 'Testing', 'Dev')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Testing'))

        env = self.env_api.create(org, 'Release', 'Testing')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Release'))
        library = self.env_api.environment_by_name(org['label'], 'Library')

        all_systems = queued_work(self.sys_api.create, 12, 2, org, library)

        for sys1 in all_systems:
            self.assertEqual(sys1['uuid'], self.sys_api.system(sys1['uuid'])['uuid'])
