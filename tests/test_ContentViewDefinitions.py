from basetest import BaseTest
from basetest import runIf

from katello.client.server import ServerRequestError
from mangonel.common import generate_name

@runIf('katello')
class TestContentViewDefinitions(BaseTest):

    def test_create_content_view_definition_1(self):
        "Creates an empty content view definition."

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

    def test_delete_content_view_definition_1(self):
        "Deletes an empty content view definition."

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

        # Delete it
        self.cvd_api.delete(cvd['id'])
        self.logger.debug("Deleted Content View Definition '%s'." % cvd['name'])
        self.assertRaises(ServerRequestError, lambda: self.cvd_api.content_view_definition(org, cvd['id']))
