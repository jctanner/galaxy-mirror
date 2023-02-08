#!/usr/bin/env python3

import datetime
import json
import os
import hashlib
import requests
import time

from logzero import logger


class RequestsResponse:
    def __init__(self, data):
        self.data = data

    @property
    def headers(self):
        return self.data['headers']

    @property
    def status_code(self):
        return self.data.get('status_code', 200)

    def json(self):
        return json.loads(self.data['text'])


class BetaScraper:

    bearer_token = None
    cache_dir = '.cache/beta'

    def __init__(self):
        self.base_url = 'https://beta-galaxy.ansible.com'

    def cached_get(self, url, prefix=''):
        logger.info(prefix + url)

        headers = {}

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        hashed = hashlib.md5(url.encode('utf-8'))
        digest = hashed.hexdigest()
        cachefile = os.path.join(self.cache_dir, digest + '.json')
        if os.path.exists(cachefile):
            with open(cachefile, 'r') as f:
                data = json.loads(f.read())
            rr = RequestsResponse(data)

            if data.get('status_code') != 404 and data.get('status_code') != 502:
                try:
                    rr.json()
                except Exception as e:
                    print(e)
                    import epdb; epdb.st()

            return rr

        success = False
        count_of_502s = 0
        while not success:
            rr = requests.get(url, headers=headers)
            logger.info('.' + str(rr.status_code))
            if rr.status_code == 404:
                success = True
                break
            if rr.status_code == 502:
                count_of_502s += 1
                if count_of_502s > 10:
                    break
                time.sleep(5)
                continue
            try:
                rr.json()
                success = True
                break
            except Exception as e:
                print(e)
                import epdb; epdb.st()

        ds = {
            'time': datetime.datetime.now().isoformat(),
            'headers': dict(rr.headers),
            'status_code': rr.status_code,
            'text': rr.text
        }
        with open(cachefile, 'w') as f:
            f.write(json.dumps(ds))
        return rr

    def scrape_collections(self):
        url = self.base_url + '/api/v3/collections/'
        headers = {}

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
        total_collections = len(collections)
        for idc,collection in enumerate(collections):

            next_url = self.base_url + collection['versions_url']
            while next_url:
                rr = self.cached_get(next_url, prefix=f'{total_collections}:{idc} - ')
                next_url = None
                if rr.status_code == 404:
                    break
                if rr.status_code == 502:
                    break
                ds = rr.json()
                if ds['links']['next']:
                    next_url = self.base_url + ds['links']['next']
                collection_versions.extend(ds['data'])

        collection_version_details = []
        total_collection_versions = len(collection_versions)
        for idcv,cv in enumerate(collection_versions):
            url = self.base_url + cv['href']
            rr = self.cached_get(url, prefix=f'{total_collection_versions}:{idcv} - ')
            if rr.status_code == 502:
                continue
            if rr.status_code == 520:
                continue
            ds = rr.json()
            collection_version_details.append(ds)

        return collection_versions


def main():

    beta_scraper = BetaScraper()
    cvs = beta_scraper.scrape_collections()

    with open('/tmp/cversions.txt', 'a') as f:
        for cv in cvs:
            href = cv['href']
            hparts = href.split('/')
            namespace = hparts[9]
            name = hparts[10]
            version = cv['version']
            row = f'beta,{namespace},{name},{version}\n'
            f.write(row)


if __name__ == "__main__":
    main()
