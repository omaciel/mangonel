#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ts=4 sw=4 expandtab ai

import argparse
import glob
import os
import subprocess
import sys

# Borrowed from https://github.com/pulp/pulp/blob/master/run-tests.py
# Find and eradicate any existing .pyc files, so they do not eradicate us!
PROJECT_DIR = os.path.abspath(os.path.curdir)

subprocess.call(['find', PROJECT_DIR, '-name', '*.pyc', '-delete'])

parser = argparse.ArgumentParser()

parser.add_argument('-s', '--host', type=str, dest='host', help='Server url')
parser.add_argument('-u', '--username', type=str, dest='username', default='admin', help='Valid system username')
parser.add_argument('-p', '--password', type=str, dest='password', default='admin', help='Valid system user password')
parser.add_argument('--project', type=str, dest='project', default='/katello', help='Project can be either "katello" or "headpin"')
parser.add_argument('--port', type=str, dest='port', default='443', help='Server port, defaults to 443')
parser.add_argument('--verbose', type=int,  choices=range(1, 6), default=1, help='Debug verbosity level')
parser.add_argument('--katello-src', type=str, dest='src', default='/usr/lib/python2.6/site-packages/katello/client/api', help='Location for Katello\'s source code.')

[options, ignored_options] = parser.parse_known_args()

os.environ['KATELLO_HOST'] = options.host
os.environ['KATELLO_USERNAME'] = options.username
os.environ['KATELLO_PASSWORD'] = options.password
os.environ['PROJECT'] = options.project
os.environ['KATELLO_PORT'] = options.port
os.environ['VERBOSITY'] = str(options.verbose)

PACKAGES = [x.split('/')[-1][:-3] for x in glob.glob("%s/*.py" % options.src) if 'init' not in x]

env = os.environ.copy()

params = [
    'nosetests',
    '--verbosity=%s' % options.verbose,
    '--with-xunit',
    '--with-coverage',
    '--cover-html',
    '--cover-erase',
    '--cover-package',
    ",".join(["katello.client.api.%s" % x for x in PACKAGES]),
]

subprocess.call(params, env=env)
