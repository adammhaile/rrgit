#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import base64
import json
import time
import argparse
import pathlib

from github import Github # pip install PyGithub
import github_release as gr # pip install githubrelease

parser = argparse.ArgumentParser()
# parser.add_argument('--nobump', action='store_true', dest='nobump', default=false)
parser.add_argument('--version', '-v', action='store', dest='version', default=None)
args = parser.parse_args()

rrgit_path = pathlib.Path(__file__).parent.absolute()

if args.version:
    VERSION = args.version
else:
    VERSION = None

REPO = 'adammhaile/rrgit'
DOWNLOAD_URL = 'https://github.com/{}/releases/download/{}/{}'

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
if not GITHUB_TOKEN:
    print('ERROR: Environment variable GITHUB_TOKEN must be set!')
    exit(1)
    
gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO)

version_data = repo.get_contents('rrgit/version.py')
if VERSION is None:
    VERSION = base64.b64decode(version_data.content).decode('ascii').replace('VERSION=', '').strip().replace("'", "")
    x, y, z = VERSION.split('.')
    z = int(z)
    z += 1
    VERSION = f'{x}.{y}.{z}'
    
VERSION_CONTENT = f"VERSION='{VERSION}'"
print('Updating version.py')
print(VERSION_CONTENT)

repo.update_file('rrgit/version.py', f'Bump to v{VERSION}', VERSION_CONTENT, version_data.sha)

print('Creating release...')

name = f'v{VERSION}'
gr.gh_release_create('adammhaile/rrgit', name, publish=True, name=name, body=name)
    
print('Complete!')