#!/usr/bin/env python3

import datetime
import json
import os
import hashlib
import requests

from logzero import logger


class RequestsResponse:
    def __init__(self, data):
        self.data = data

    @property
    def headers(self):
        return self.data['headers']

    def json(self):
        return json.loads(self.data['text'])


class CRCScraper:

    bearer_token = None
    cache_dir = '.cache/crc'

    def __init__(self, username=None, password=None, refresh_token=None):
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        if self.refresh_token:
            self.grant_type = 'refresh_token'
        else:
            self.grant_type = 'password'

        self.base_url = 'https://console.redhat.com'
        self.auth_url = 'https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token'

        if self.grant_type == 'refresh_token':
            self.refresh_bearer_token()

    def refresh_bearer_token(self):
        self.bearer_token = self.get_bearer_token(grant_type=self.grant_type)

    @property
    def auth_headers(self):
        if self.bearer_token:
            return {'Authorization': f'Bearer {self.bearer_token}'}
        return {}

    def cached_get(self, url):
        logger.info(url)
        headers = self.auth_headers

        cachedir = '/tmp/crc.cache'
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        hashed = hashlib.md5(url.encode('utf-8'))
        digest = hashed.hexdigest()
        cachefile = os.path.join(self.cache_dir, digest + '.json')
        if os.path.exists(cachefile):
            with open(cachefile, 'r') as f:
                data = json.loads(f.read())

            if 'Invalid JWT token' not in data['text']:
                rr = RequestsResponse(data)
                try:
                    rr.json()
                except Exception as e:
                    print(e)
                    import epdb; epdb.st()
                return rr

        success = False
        while not success:
            rr = requests.get(url, headers=headers)
            try:
                rr.json()
                success = True
                break
            except Exception as e:
                print(e)
                if 'Invalid JWT token' in rr.text:
                    self.refresh_bearer_token()

        ds = {
            'time': datetime.datetime.now().isoformat(),
            'headers': dict(rr.headers),
            'text': rr.text
        }

        with open(cachefile, 'w') as f:
            f.write(json.dumps(ds))

        return rr

    def get_bearer_token(self, grant_type='password'):
        # payload
        #   grant_type=refresh_token&client_id=cloud-services&refresh_token=abcdefghijklmnopqrstuvwxyz1234567894
        # POST
        # auth_url
        #   'https://mocks-keycloak-ephemeral-ydabku.apps.c-rh-c-eph.8p0c.p1.openshiftapps.com
        #       /auth/realms/redhat-external/protocol/openid-connect/token'

        logger.info(f"getting bearer token with {grant_type} grant")

        if grant_type != 'password':
            # Production workflows on CRC will use refresh_tokens ...
            payload = {
                'grant_type': 'refresh_token',
                'client_id': 'cloud-services',
                'refresh_token': self.refresh_token
            }
        else:
            # ephemeral/keycloak doesn't have any way for us to set pre-defined
            # refresh tokens, so we have to use a password grant instead ...
            payload = {
                'grant_type': 'password',
                'client_id': 'cloud-services',
                'username': self.username,
                'password': self.password,
            }

        session = requests.Session()
        rr = session.post(
            self.auth_url,
            headers={
                'User-Agent': 'ansible-galaxy/2.10.17 (Linux; python:3.10.6)'
            },
            data=payload,
            verify=False
        )

        # construct a helpful error message ...
        msg = (
            self.auth_url
            + '\n'
            + str(payload)
            + '\n'
            + str(rr.status_code)
            + '\n'
            + rr.text
        )

        # bail out early if auth failed ...
        assert rr.status_code >= 200 and rr.status_code < 300, msg
        assert rr.headers.get('Content-Type') == 'application/json', msg
        assert 'access_token' in rr.json(), msg

        ds = rr.json()
        access_token = ds['access_token']
        return access_token


    def scrape_collections(self):
        url = self.base_url + '/api/automation-hub/v3/collections/'
        headers = self.auth_headers

        collections = []
        next_url = url
        while next_url:
            rr = self.cached_get(next_url)
            next_url = None
            ds = rr.json()
            if ds['links']['next']:
                next_url = self.base_url + ds['links']['next']
            collections.extend(ds['data'])

        collection_versions = []
        for collection in collections:
            next_url = self.base_url + collection['versions_url']
            while next_url:
                rr = self.cached_get(next_url)
                next_url = None
                ds = rr.json()
                if ds['links']['next']:
                    next_url = self.base_url + ds['links']['next']
                collection_versions.extend(ds['data'])

        collection_version_details = []
        for cv in collection_versions:
            url = self.base_url + cv['href']
            rr = self.cached_get(url)
            ds = rr.json()
            collection_version_details.append(ds)

        return collection_versions


def main():

    refresh_token = os.environ.get('CRC_REFRESH_TOKEN')
    crcscraper = CRCScraper(refresh_token=refresh_token)
    cvs = crcscraper.scrape_collections()

    with open('/tmp/cversions.txt', 'a') as f:
        for cv in cvs:
            href = cv['href']
            hparts = href.split('/')
            namespace = hparts[10]
            name = hparts[11]
            version = cv['version']
            row = f'crc,{namespace},{name},{version}\n'
            f.write(row)


if __name__ == "__main__":
    main()
