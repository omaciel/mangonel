#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from basetest import BaseTest

from katello.client.server import ServerRequestError
from mangonel.common import generate_name

class TestUsers(BaseTest):

    def test_create_user_1(self):
        "Creates a new system user."

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

    def test_create_user_2(self):
        "Creates a new system user with specific arguments."

        username = "user-%s" % generate_name(4)
        userpass = generate_name(8)
        useremail = "%s@example.com" % username

        user = self.user_api.create(username, userpass, useremail)
        self.assertEqual(user['username'], username)
        self.assertEqual(user['email'], useremail)

    def test_create_user_3(self):
        "Create user with default locale"

        user = self.user_api.create(default_loc='pt-BR')
        self.assertEqual(user, self.user_api.user(user['id']))

        user = self.user_api.user(user['id'])
        self.assertEqual('pt-BR', user['preferences']['user']['locale'])

    def test_create_user_4(self):
        "Re-creates system user."

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

        self.assertRaises(ServerRequestError, lambda: self.user_api.create(name=user['username']))

    def test_invalid_usernames(self):
        "Fail username validation"

        username = "user-%s" % generate_name(4)

        names = [
            " ",
            " " + "user-%s" % generate_name(4),
            "user-%s" % generate_name(4) + " ",
            generate_name(2,2),
            generate_name(129),
            ]

        for name in names:
            self.assertRaises(ServerRequestError, lambda: self.user_api.create(name=name))

    def test_valid_usernames(self):
        "Success username"

        names = [
            generate_name(128),
            "user-%s" % generate_name(4),
            "user.%s" % generate_name(2),
            "user-%s@example.com" % generate_name(4),
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

        for name in names:
            user = self.user_api.create(name=name)
            self.assertEqual(user, self.user_api.user(user['id']))

    def test_update_user_email_and_succeed_1(self):
        "Creates and updates a system user's email."

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

        self.user_api.update(user['id'], **{'email': 'changed@example.com'})
        user = self.user_api.user(user['id'])
        self.assertEqual(user['email'], 'changed@example.com')

    def test_update_user_email_and_fail_1(self):
        "Creates and updates a system user's email."

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

        self.assertRaises(ServerRequestError, lambda: self.user_api.update(user['id'], **{'email': ' '}))

        # Nothing should have changed
        self.assertEqual(user, self.user_api.user(user['id']))

    def test_update_user_locale_1(self):
        "Creates user and updates the default locale"

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

        self.user_api.update(user['id'], **{'default_locale': 'pt-BR'})
        user = self.user_api.user(user['id'])
        self.assertEqual('pt-BR', user['preferences']['user']['locale'])


    def test_delete_user_1(self):
        "Creates and deletes a system user."

        user = self.user_api.create()
        self.assertEqual(user, self.user_api.user(user['id']))

        self.user_api.delete(user['id'])
        self.assertRaises(ServerRequestError, lambda: self.user_api.user(user['id']))
