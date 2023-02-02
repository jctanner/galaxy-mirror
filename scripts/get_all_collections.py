#!/usr/bin/env python3

import argparse
import datetime
import os
import json

import requests
from logzero import logger


def scrape_collections(baseurl=None):
    collections = []
    next_url = baseurl + '/api/v2/collections'
    while next_url:
        logger.info(next_url)
        rr = requests.get(next_url)
        ds = rr.json()

        collections.extend(ds['results'])

        if ds['next'] is None:
            break
        next_url = baseurl + ds['next']


    collections = sorted(collections, key=lambda x: x['modified'], reverse=True)
    collection_versions = []
    for idc,col in enumerate(collections):

        cversion_urls = []
        next_url = col['versions_url']
        while next_url:

            logger.info(next_url)
            rr = requests.get(next_url)
            ds = rr.json()
            cversion_urls.extend([x['href'] for x in ds['results']])
            if ds['next'] is None:
                break
            next_url = ds['next']

        for idv,cvurl in enumerate(cversion_urls):

            logger.info(f' {len(collections)}|{idc} - {len(cversion_urls)}|{idv} - {cvurl}')
            rr = requests.get(cvurl)
            ds = rr.json()
            collection_versions.append(ds)

    import epdb; epdb.st()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseurl')
    args = parser.parse_args()
    scrape_collections(baseurl=args.baseurl)
