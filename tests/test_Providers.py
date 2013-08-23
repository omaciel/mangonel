from basetest import BaseTest
from basetest import runIf

from katello.client.server import ServerRequestError
from mangonel.common import generate_name
from mangonel.common import valid_names_list
from mangonel.common import invalid_names_list
from mangonel.common import wait_for_task

class TestProviders(BaseTest):

    def _generic_organization(self):
        "Generates a new organization using generic default values"

        org = self.org_api.create()
        self.logger.info("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        return (org, library)

    @runIf('katello')
    def test_create_provider_1(self):
        "Creates a basic provider"

        (org, env) = self._generic_organization()

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

    @runIf('katello')
    def test_delete_provider_1(self):
        "Creates a basic provider, then deletes it"

        (org, env) = self._generic_organization()

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        self.prv_api.delete(prv['id'])
        self.logger.info("Deleted custom provider %s" % prv['name'])
        self.assertRaises(ServerRequestError, lambda: self.prv_api.provider(prv['id']))

    def test_delete_rh_provider_1(self):
        "Cannot delete the RH provider"

        (org, env) = self._generic_organization()

        rh_provider = self.prv_api.provider_by_name(org['label'], 'Red Hat')
        self.assertRaises(ServerRequestError, lambda: self.prv_api.delete(rh_provider['id']))

    @runIf('katello')
    def test_update_provider_1(self):
        "Updates the provider's name"

        (org, env) = self._generic_organization()

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        new_name = generate_name()
        self.prv_api.update(prv['id'], new_name, None, None)
        updt_prv = self.prv_api.provider(prv['id'])
        self.assertEqual(new_name, updt_prv['name'])

    @runIf('katello')
    def test_update_provider_2(self):
        "Updates the provider's description"

        (org, env) = self._generic_organization()

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        new_description = "Updated descritpion %s" % generate_name()
        self.prv_api.update(prv['id'], None, new_description, None)
        updt_prv = self.prv_api.provider(prv['id'])
        self.assertEqual(new_description, updt_prv['description'])

    @runIf('katello')
    def test_update_provider_3(self):
        "Updates the provider's repo url"

        (org, env) = self._generic_organization()

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        new_url = 'http://fedorapeople.org/groups/katello/releases/yum/nightly/RHEL/6Server/x86_64/'
        self.prv_api.update(prv['id'], None, None, new_url)
        updt_prv = self.prv_api.provider(prv['id'])
        self.assertEqual(new_url, updt_prv['repository_url'])

    @runIf('katello')
    def test_providers_by_org_1(self):
        "Fetches only the providers for an organization"

        (org, env) = self._generic_organization()

        # No custom providers yet, only Red Hat 'type' exists
        self.assertEqual(len(self.prv_api.providers_by_org(org)), 1)

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        # One CUSTOM provider + RH
        self.assertEqual(len(self.prv_api.providers_by_org(org)), 2)

        prv = self.prv_api.create(org)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))

        # Two CUSTOM providers + RH
        self.assertEqual(len(self.prv_api.providers_by_org(org)), 3)

        # Delete one provider
        self.prv_api.delete(prv['id'])

        # Back to only one CUSTOM provider + RH
        self.assertEqual(len(self.prv_api.providers_by_org(org)), 2)

    def test_provider_by_name_1(self):
        "Fetches the Red Hat provider by name"

        (org1, env1) = self._generic_organization()
        (org2, env2) = self._generic_organization()

        self.assertTrue(self.prv_api.provider_by_name(org1['label'], 'Red Hat'))

        self.assertTrue(self.prv_api.provider_by_name(org2['label'], 'Red Hat'))

        self.assertFalse(self.prv_api.provider_by_name(org1['label'], 'Foo'))

    @runIf('katello')
    def test_provider_by_name_2(self):
        "Fetches providers by name"

        (org1, env1) = self._generic_organization()
        (org2, env2) = self._generic_organization()

        prv1 = self.prv_api.create(org1)
        self.logger.info("Created custom provider %s" % prv1['name'])
        self.assertEqual(prv1, self.prv_api.provider(prv1['id']))

        prv2 = self.prv_api.create(org2)
        self.logger.info("Created custom provider %s" % prv2['name'])
        self.assertEqual(prv2, self.prv_api.provider(prv2['id']))

        prv = self.prv_api.provider_by_name(org1['label'], prv1['name'])
        self.assertEqual(prv1, prv)

        prv = self.prv_api.provider_by_name(org2['label'], prv2['name'])
        self.assertEqual(prv2, prv)

        prv = self.prv_api.provider_by_name(org1['label'], prv2['name'])
        self.assertEqual(prv, None)

    @runIf('katello')
    def test_repo_discovery_1(self):
        "Repo discovery"

        (org, env) = self._generic_organization()

        repo_url = 'http://fedorapeople.org/groups/katello/releases/yum/nightly'

        prv = self.prv_api.create(org, url=repo_url)
        self.logger.info("Created custom provider %s" % prv['name'])
        self.assertEqual(prv, self.prv_api.provider(prv['id']))
        self.assertEqual(len(prv['discovered_repos']), 0)

        # Discovery
        task_id = self.prv_api.repo_discovery(prv['id'], repo_url)
        task = wait_for_task(task_id['uuid'])
        self.assertNotEqual(task, None)

        prv = self.prv_api.provider(prv['id'])
        self.assertTrue(len(prv['discovered_repos']) > 0)
