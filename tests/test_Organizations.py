#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from basetest import BaseTest

from katello.client.server import ServerRequestError
from mangonel.common import generate_name
from mangonel.common import valid_names_list
from mangonel.common import invalid_names_list

class TestOrganizations(BaseTest):

    def test_create_org1(self):
        "Creates a new organization."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

    def test_create_org2(self):
        "Creates a new organization and then deletes it."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        self.logger.info("Deleting organization %s" % org['name'])
        self.org_api.delete(org['name'])
        self.assertRaises(ServerRequestError, lambda: self.org_api.organization(org['name']))

    def test_create_org3(self):
        "Creates a new organization with an initial environment."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

        env = self.env_api.create(org, 'Dev', 'Library')
        self.logger.debug("Created environemt %s" % env['name'])
        self.assertEqual(env, self.env_api.environment_by_name(org['label'], 'Dev'))

    def test_create_org4(self):
        "Creates a new organization with several environments."

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

    def test_create_org5(self):
        "Org name and labels are unique across the server."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')
        self.assertRaises(ServerRequestError, lambda: self.org_api.create(name=org['name'], label=org['label']))
        self.assertRaises(ServerRequestError, lambda: self.org_api.create(name=org['name'], label=generate_name()))
        self.assertRaises(ServerRequestError, lambda: self.org_api.create(name=generate_name(), label=org['label']))

    def test_delete_org_1(self):
        "Delete organizations with valid names."

        for name in valid_names_list():
           org = self.org_api.create(name=name)
           self.logger.debug("Created organization %s" % org['name'])
           self.assertEqual(org, self.org_api.organization(org['name']), 'Failed to create and retrieve org.')

           self.logger.info("Deleting organization %s" % org['name'])
           self.org_api.delete(org['name'])
           self.assertRaises(ServerRequestError, lambda: self.org_api.organization(org['name']))

    def test_invalid_org_names(self):
        "These organization names are not valid."

        for name in invalid_names_list():
            self.assertRaises(ServerRequestError, lambda: self.org_api.create(name=name, label="label-%s" % generate_name(2)))

    def test_valid_org_names(self):
        "These organization names are valid."

        for name in valid_names_list():
            org = self.org_api.create(name=name, label="label-%s" % generate_name(2))
            self.logger.debug("Created organization %s" % org['name'])
            self.assertEqual(org, self.org_api.organization(org['label']))

    def test_valid_org_labels(self):
        "These organization labels are valid."

        org_labels = [
            " ",
            None,
            "label-invalid-%s" % generate_name(2),
            generate_name(128),
            '_%s' % "label-invalid-%s" % generate_name(2),
            '%s_' % "label-invalid-%s" % generate_name(2),
            'label_%s' % "label-invalid-%s" % generate_name(2),
            ]

        for label in org_labels:
            org = self.org_api.create(name=generate_name(3), label=label)
            self.logger.debug("Created organization %s" % org['name'])
            self.assertEqual(org, self.org_api.organization(org['label']))

    def test_invalid_org_labels(self):
        "These organization labels are not valid."

        org_labels = [
            " " + "label-invalid-%s" % generate_name(2),
            "label-invalid-%s" % generate_name(2) + " ",
            generate_name(129),
            '<bold>%s</bold>' % "label-invalid-%s" % generate_name(2),
            ]

        for label in org_labels:
            self.assertRaises(ServerRequestError, lambda: self.org_api.create(name=generate_name(3), label=label))

    def test_update_org_description(self):
        "Update the description for an organization."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['label']))

        description = "New description: %s" % generate_name()
        self.org_api.update(org['label'], {'description': description})

        updated = self.org_api.organization(org['label'])
        self.assertEqual(description, updated['description'])
        self.assertNotEqual(org['description'], updated['description'])

    def test_fetch_all_organizations(self):
        "Checks that total of organizations updates with addition/deletion."

        before_tot = len(self.org_api.organizations())

        # Add a new organization
        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['label']))

        self.assertEqual(before_tot + 1, len(self.org_api.organizations()))

        # Now delete an organization
        self.org_api.delete(org['label'])
        self.assertEqual(before_tot, len(self.org_api.organizations()))

    def test_download_uebercert(self):
        "Downloads the uebercert for an organization."

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['label']))

        uebercert = self.org_api.uebercert(org['label'])
        #TODO: perform a check

    def test_attach_all_systems(self):

        org = self.org_api.create()
        self.logger.debug("Created organization %s" % org['name'])
        self.assertEqual(org, self.org_api.organization(org['label']))

        task = self.org_api.attach_all_systems(org['label'])
        #TODO: check that task finishes
