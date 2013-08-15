from basetest import BaseTest

from katello.client.server import ServerRequestError
from mangonel.common import generate_name

class TestActivationKeys(BaseTest):

    def _generic_activation_key(self):
        "Generates a new activationkey using generic default values"

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='Default Organization View')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

        return (org, library, ak1)

    def test_update_ak_1(self):
        "Updates the environment and content view for existing activationkey"

        (org, env, ak) = self._generic_activation_key()

        # Content view for new environment

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
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
        self.prv_api.sync(prv['id'])
        self.assertEqual(self.prv_api.provider(prv['id'])['sync_state'], 'finished')
        self.logger.debug("Finished synchronizing Provider1")

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")
        prods = self.cvd_api.update_products(org, cvd['id'], prd)
        self.logger.debug("Added %s to Content View Definition" % prd['name'])

        task = self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        self.assertTrue(task)
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

        # Changeset
        chs = self.chs_api.create(org, env1, 'Promote01')
        self.logger.debug("Created promotion changeset Promote01")
        self.chs_api.add_content(chs['id'], pcvd)
        self.logger.debug("Added %s to changeset" % pcvd['name'])
        task = self.chs_api.apply(chs['id'])
        self.assertTrue(task)

        self.ak_api.update(org['label'], ak['id'], env1['id'], None, None, None, pcvd['id'])
        ak = self.ak_api.activation_key(org, ak['id'])
        self.assertEqual(env1['id'], ak['environment_id'])
        self.assertEqual(pcvd['id'], ak['content_view_id'])

    def test_update_ak_2(self):
        "Updates the name for existing activationkey"

        (org, env, ak) = self._generic_activation_key()

        new_name = generate_name()
        self.ak_api.update(org['label'], ak['id'], env['id'], new_name, None, None, None)
        ak = self.ak_api.activation_key(org, ak['id'])
        self.assertEqual(new_name, ak['name'])

    def test_update_ak_3(self):
        "Updates the description for existing activationkey"

        (org, env, ak) = self._generic_activation_key()

        new_description = "Manually changed description %s" % generate_name()
        self.ak_api.update(org['label'], ak['id'], env['id'], None, new_description, None, None)
        ak = self.ak_api.activation_key(org, ak['id'])
        self.assertEqual(new_description, ak['description'])

    def test_update_ak_4(self):
        "Updates the usage limit for existing activationkey"

        (org, env, ak) = self._generic_activation_key()

        self.ak_api.update(org['label'], ak['id'], env['id'], None, None, 5, None)
        ak = self.ak_api.activation_key(org, ak['id'])
        self.assertEqual(5, ak['usage_limit'])

    def test_get_ak_1(self):
        "Tries to fetch an invalid activationkey."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        self.assertRaises(ServerRequestError, lambda: self.ak_api.activation_key(org, 10000))

    def test_create_ak_1(self):
        "Assures that a content view is passed during creation."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        self.assertRaises(ServerRequestError, lambda: self.ak_api.create(env1))

    def test_create_ak_2(self):
        "Creates a new activationkey against default content view."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='Default Organization View')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

    def test_create_ak_3(self):
        "Creates a new activationkey with no content."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")

        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

    def test_add_pool(self):
        "Creates a new activationkey and adds a pool."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")

        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

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
        self.prv_api.sync(prv['id'])
        self.assertEqual(self.prv_api.provider(prv['id'])['sync_state'], 'finished')
        self.logger.debug("Finished synchronizing Provider1")

        #TODO: There seems to be a delay between sync and pools being available
        pools = self.org_api.pools(org['label'])

        for pool in pools:
            self.ak_api.add_pool(org, ak1['id'], pool['id'])
            self.assertTrue(self.ak_api.has_pool(org, ak1['id'], pool['id']))
            self.logger.debug("Added pool id '%s'' to activationkey '%s'" % (pool['id'], ak1['name']))

    def test_remove_pool(self):
        "Creates a new activationkey, adds a pool and then removes it."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        cvd = self.cvd_api.create(org, 'CVD1')
        self.logger.debug("Created Content View Definition CVD1")

        self.cvd_api.publish(org, cvd['id'], 'PublishedCVD1')
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD1')
        self.logger.debug("Published Content View PublishedCVD1")

        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

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
        self.prv_api.sync(prv['id'])
        self.assertEqual(self.prv_api.provider(prv['id'])['sync_state'], 'finished')
        self.logger.debug("Finished synchronizing Provider1")

        #TODO: There seems to be a delay between sync and pools being available
        pools = self.org_api.pools(org['label'])

        for pool in pools:
            self.ak_api.add_pool(org, ak1['id'], pool['id'])
            self.assertTrue(self.ak_api.has_pool(org, ak1['id'], pool['id']))
            self.logger.debug("Added pool id '%s'' to activationkey '%s'" % (pool['id'], ak1['name']))

        # Now, remove pools
        for pool in pools:
            self.ak_api.remove_pool(org, ak1['id'], pool['id'])
            self.assertFalse(self.ak_api.has_pool(org, ak1['id'], pool['id']))

    def test_activation_key_by_organization(self):

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='Default Organization View')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        # First activation key
        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

        aks = self.ak_api.activation_keys_by_organization(org['label'])
        self.assertEqual(len(aks), 1)

        # Second activation key
        ak2 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak2['name'])
        self.assertEqual(ak2, self.ak_api.activation_key(org, ak2['id']))

        aks = self.ak_api.activation_keys_by_organization(org['label'])
        self.assertEqual(len(aks), 2)

        # Can get activation key by name
        aks = self.ak_api.activation_keys_by_organization(org['label'], ak1['name'])
        self.assertEqual(len(aks), 1)
        self.assertEqual(ak1, aks[0])

    def test_activation_key_by_environment(self):

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='Default Organization View')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        # First activation key
        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

        # Second activation key
        ak2 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak2['name'])
        self.assertEqual(ak2, self.ak_api.activation_key(org, ak2['id']))

        aks = self.ak_api.activation_keys_by_environment(library['id'])
        self.assertEqual(len(aks), 2)

        # Now, add activation key to different environment

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
        self.prv_api.sync(prv['id'])
        self.assertEqual(self.prv_api.provider(prv['id'])['sync_state'], 'finished')
        self.logger.debug("Finished synchronizing Provider1")

        cvd = self.cvd_api.create(org, generate_name())
        self.logger.debug("Created Content View Definition CVD1")
        prods = self.cvd_api.update_products(org, cvd['id'], prd)
        self.logger.debug("Added %s to Content View Definition" % prd['name'])

        task = self.cvd_api.publish(org, cvd['id'], 'PublishedCVD2')
        self.assertTrue(task)
        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='PublishedCVD2')
        self.logger.debug("Published Content View PublishedCVD1")

        # Changeset
        chs = self.chs_api.create(org, env1, 'Promote01')
        self.logger.debug("Created promotion changeset Promote01")
        self.chs_api.add_content(chs['id'], pcvd)
        self.logger.debug("Added %s to changeset" % pcvd['name'])
        task = self.chs_api.apply(chs['id'])
        self.assertTrue(task)

        ak3 = self.ak_api.create(env1, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak3['name'])
        self.assertEqual(ak3, self.ak_api.activation_key(org, ak3['id']))

        aks = self.ak_api.activation_keys_by_environment(env1['id'])
        self.assertEqual(len(aks), 1)

    def test_delete_activation_key(self):

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env1 = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org['label'], 'Dev'))

        pcvd = self.cv_api.content_views_by_label_name_or_id(org, name='Default Organization View')

        library = self.env_api.environment_by_name(org['label'], 'Library')

        ak1 = self.ak_api.create(library, cvId=pcvd['id'])
        self.logger.debug("Created activationkey %s" % ak1['name'])
        self.assertEqual(ak1, self.ak_api.activation_key(org, ak1['id']))

        # Now, delete it
        self.ak_api.delete(org, ak1['id'])
        self.assertRaises(ServerRequestError, lambda: self.ak_api.activation_key(org, ak1['id']))
