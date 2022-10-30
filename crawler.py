#!/usr/bin/env python

import datetime
import requests
import subprocess


perfmap = {}


def paginate(next_url):
    base_url = 'http://localhost:8080'
    to_fetch = []
    while next_url:
        print(next_url)
        t1 = datetime.datetime.now()
        rr = requests.get(next_url)
        t2 = datetime.datetime.now()
        delta = t2 - t1
        perfmap[next_url] = delta

        if rr.status_code != 200:
            parts = next_url.split('=')
            pagenum = int(parts[1]) + 1
            next_url = parts[0] + '=' + str(pagenum)
            continue

        ds = rr.json()
        if ds.get('results'):
            for result in ds['results']:
                if isinstance(result, dict) and result.get('href'):
                    to_fetch.append(base_url + result['href'])

        if not ds.get('next_link'):
            break
        next_url = base_url + ds['next_link']

    if to_fetch:
        for tf in to_fetch:
            print(tf)
            rr = requests.get(tf)
            ds = rr.json()
            if 'download_url' in ds:
                dl_url = base_url + ds['download_url']
                subprocess.run(f'curl -o /tmp/test {dl_url}', shell=True)
                #import epdb; epdb.st()


def crawl_collections():
    base_url = 'http://localhost:8080'
    next_url = base_url + '/api/v2/collections/'

    collections = []
    while next_url:
        print(next_url)
        rr = requests.get(next_url)
        ds = rr.json()
        collections.extend(ds['results'])
        if ds.get('next_link') is None:
            break
        next_url = base_url + ds['next_link']

    for collection in collections:
        href = base_url + collection['href']
        print(href)
        rr1 = requests.get(href)
        paginate(base_url + collection['versions_url'])
        #import epdb; epdb.st()


def crawl_roles():
    base_url = 'http://localhost:8080'

    roles = []

    next_url = base_url + '/api/v1/roles'
    while next_url:
        print(next_url)
        t1 = datetime.datetime.now()
        rr = requests.get(next_url)
        t2 = datetime.datetime.now()
        delta = t2 - t1
        perfmap[next_url] = delta
        print(delta)

        if rr.status_code != 200:
            parts = next_url.split('=')
            pagenum = int(parts[1]) + 1
            next_url = parts[0] + '=' + str(pagenum)
            continue

        ds = rr.json()
        if not ds.get('next_link'):
            break
        next_url = base_url + ds['next_link']
        roles.extend(ds['results'])

    # iterate each role ...
    for idr,role in enumerate(roles):
        role_url = base_url + role['url']
        print(f'{len(roles)}|{idr} {role_url}')
        t1 = datetime.datetime.now()
        rr2 = requests.get(role_url)
        t2 = datetime.datetime.now()
        delta = t2 - t1
        perfmap[role_url] = delta

        ds2 = rr2.json()
        paginate(base_url + role['url'] + 'versions/')


def main():

    #crawl_roles()
    crawl_collections()
    import epdb; epdb.st()


if __name__ == "__main__":
    main()
