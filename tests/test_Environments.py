#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from basetest import BaseTest
from basetest import runIf

from katello.client.server import ServerRequestError
from mangonel.common import generate_name

@runIf('katello')
class TestEnvironments(BaseTest):

    def _create_org(self):
        "Creates generic organizations."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        return org

    def test_create_env_1(self):
        "Creates a new environment."

        org = self._create_org()

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

    def test_create_env_2(self):
        "Cannot create two environments with same name."

        org = self._create_org()

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        self.assertRaises(ServerRequestError, lambda: self.env_api.create(org, 'Dev', 'Library'))

    def test_create_env_3(self):
        "Cannot create two environments with same label."

        org = self._create_org()

        env = self.env_api.create(org, 'Dev', 'Library', label='Dev')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        self.assertRaises(ServerRequestError, lambda: self.env_api.create(org, 'QE', 'Library', label='Dev'))

    def test_delete_env_1(self):
        "Deletes a new environment."

        org = self._create_org()

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

        self.env_api.delete(org['label'], env['id'])
        self.assertEqual(None, self.env_api.environment_by_name(org['label'], 'Dev'))

    def test_delete_env_2(self):
        "Cannot delete the Library environment."

        org = self._create_org()

        env = self.env_api.library_by_org(org['label'])
        self.assertTrue(env['library'])

        # Delete Library environment
        self.assertRaises(ServerRequestError, lambda: self.env_api.delete(org['label'], env['id']))

    def test_library_not_allowed_1(self):
        "Library is not an allowed environment name."

        org = self._create_org()

        self.assertRaises(ServerRequestError, lambda: self.env_api.create(org, 'Library', 'Library'))

    def test_library_not_allowed_2(self):
        "Library is not an allowed environment label."

        org = self._create_org()

        self.assertRaises(ServerRequestError, lambda: self.env_api.create(org, 'Dev', 'Library', label='Library'))

    def test_library_by_org(self):
        "Fetches library environment by organization."

        org = self._create_org()

        env = self.env_api.library_by_org(org['label'])
        self.assertTrue(env['library'])

    def test_environments_by_org(self):
        "Fetches all environments for organization"

        org1 = self._create_org()

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Dev'))

        env = self.env_api.create(org1, 'Test', 'Dev')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Test'))

        env = self.env_api.create(org1, 'Release', 'Test')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Release'))

        self.assertEqual(len(self.env_api.environments_by_org(org1['label'])), 4)

    def test_multiple_paths(self):
        "All environments have Library as prior environment"

        org1 = self._create_org()

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Dev'))
        self.assertEqual("Library", env['prior'])

        env = self.env_api.create(org1, 'Test', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Test'))
        self.assertEqual("Library", env['prior'])

        env = self.env_api.create(org1, 'Release', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Release'))
        self.assertEqual("Library", env['prior'])

    def test_environment_by_org(self):
        "Fetches environment from organization."

        org1 = self._create_org()

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_org(org1['label'], env['id']))
        self.assertEqual("Library", env['prior'])

    def test_environments_by_org(self):
        "Fetches environment by organization."

        org1 = self._create_org()

        # There should be 1 environment by default: Library
        environments = self.env_api.environments_by_org(org1['label'])
        self.assertEqual(len(environments), 1)
        self.assertEqual("Library", environments[0]['name'])

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Dev'))
        self.assertEqual("Library", env['prior'])

        # There should be one more environment now.
        self.assertEqual(len(self.env_api.environments_by_org(org1['label'])), 2)

    def test_update_environment_1(self):
        "Updates the environment name."

        org1 = self._create_org()

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Dev'))
        self.assertEqual("Library", env['prior'])

        new_name = "updated-%s" % generate_name(4)
        env = self.env_api.update(org1['label'], env['id'], name=new_name, description=None, priorId=None)
        env = self.env_api.environment_by_name(org1['label'], new_name)
        self.assertEqual(new_name, env['name'])

        # Try to update name to a blank space
        self.assertRaises(ServerRequestError, lambda: self.env_api.update(org1['label'], env['id'], name='', description=None, priorId=None))
        # Make sure nothing has changed
        env = self.env_api.environment_by_name(org1['label'], new_name)
        self.assertEqual(new_name, env['name'])

    def test_update_environment_2(self):
        "Updates the environment description."

        org1 = self._create_org()

        env = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org1['label'], 'Dev'))
        self.assertEqual("Library", env['prior'])

        new_description = "updated-%s" % generate_name(4)
        env = self.env_api.update(org1['label'], env['id'], name=None, description=new_description, priorId=None)
        env = self.env_api.environment_by_name(org1['label'], env['name'])
        self.assertEqual(new_description, env['description'])

        # Try to update description to a blank space
        self.env_api.update(org1['label'], env['id'], name=None, description='', priorId=None)
        # Make sure description has changed
        env = self.env_api.environment_by_name(org1['label'], env['name'])
        self.assertEqual('', env['description'])

    def test_update_environment_3(self):
        "Updates the environment prior environment."

        org1 = self._create_org()

        env1 = self.env_api.create(org1, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env1['name'])
        self.assertEqual(env1, self.env_api.environment_by_name(org1['label'], 'Dev'))
        self.assertEqual("Library", env1['prior'])

        env2 = self.env_api.create(org1, 'QE', 'Library')
        self.logger.debug("Created environemt %s" % env2['name'])
        self.assertEqual(env2, self.env_api.environment_by_name(org1['label'], 'QE'))
        self.assertEqual("Library", env2['prior'])

        self.env_api.update(org1['label'], env2['id'], name=None, description=None, priorId=env1['id'])
        env = self.env_api.environment_by_name(org1['label'], env2['name'])
        self.assertEqual(env1['name'], env['prior'])

    def test_valid_names(self):
        "Success environment names"

        names = [
            generate_name(2, 2),
            generate_name(255),
            "env-%s" % generate_name(4),
            "env.%s" % generate_name(2),
            "env-%s@example.com" % generate_name(4),
            u"նոր օգտվող-%s" % generate_name(2),
            u"新用戶-%s" % generate_name(2),
            u"नए उपयोगकर्ता-%s" % generate_name(2),
            u"нового пользователя-%s" % generate_name(2),
            u"uusi käyttäjä-%s" % generate_name(2),
            u"νέος χρήστης-%s" % generate_name(2),
            "foo@!#$^&*( ) %s" % generate_name(),
            "<blink>%s</blink>" % generate_name(),
            "bar+{}|\"?hi %s" % generate_name(),
            ]

        org = self._create_org()

        for name in names:

            self.logger.debug(name)
            env = self.env_api.create(org, name=name)
            self.assertEqual(env, self.env_api.environment_by_name(org['label'], name))

    def test_invalid_names(self):
        "Invalid names"

        names = [
                " ",
                " " + "env-%s" % generate_name(4),
                "env-%s" % generate_name(4) + " ",
                generate_name(256),
                ]

        org = self._create_org()

        for name in names:

            self.logger.debug(name)
            self.assertRaises(ServerRequestError, lambda: self.env_api.create(org, name=name))
