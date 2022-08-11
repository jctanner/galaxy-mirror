#!/usr/bin/env python3

import datetime
import os
import json
from logzero import logger

from lib.mirror import get_cached_url
from lib.mirror import BASEURL

TOKEN = os.environ.get('GALAXY_TOKEN')


'''
repo_imports = []
next_url = 'https://galaxy.ansible.com/api/v1/repositories'
while next_url:
    res = get_cached_url(next_url, logger=logger)
    ds = json.loads(res.data)
    if ds['next'] is None:
        break
    next_url = BASEURL + '/api/v1' + ds['next']

    for repo in ds['results']:
        latest_import = repo['summary_fields']['latest_import']
        next_imports_url = BASEURL + repo['related']['imports']
        while next_imports_url:
            ires = get_cached_url(next_imports_url, logger=logger)
            ids = json.loads(ires.data)
            if ids['next'] is None:
                break
            next_imports_url = BASEURL + '/api/v1' + ids['next']
            repo_imports.extend(ids['results'])
            for rimport in ids['results']:
                logger.info(f'import {repo["name"]} {rimport["id"]} {rimport["commit_url"]}')
                #import epdb; epdb.st()

    #import epdb; epdb.st()
'''



imports = {}
fetched = set()
max_count = None
min_bad = None
counter = 1
increment = 1000
while True:

    print(counter)
    if counter in fetched:
        break
    fetched.add(counter)

    # https://galaxy.ansible.com/api/v2/collection-imports/17
    imports_url = BASEURL + '/api/v2/collection-imports/' + str(counter)
    res = get_cached_url(imports_url, logger=logger, token=TOKEN, refresh=True)
    print(res)
    if res.status_code == 404:
        if min_bad is None or counter < min_bad:
            min_bad = counter
        counter = (counter - increment) + 1
        increment = 1
        continue
    else:
        if max_count is None or counter > max_count:
            max_count = counter

    logger.info(res)
    ds = json.loads(res.data)
    imports[counter] = ds

    increment *= 2
    counter += increment

durations = []
to_fetch = list(range(max_count, 0, -1))
for tf in to_fetch[:2000]:
    #if tf in imports:
    #    continue
    imports_url = BASEURL + '/api/v2/collection-imports/' + str(tf)
    res = get_cached_url(imports_url, logger=logger, token=TOKEN, refresh=False)
    ds = json.loads(res.data)
    if ds.get('code') == 'not_found':
        continue
    imports[tf] = ds
    #if 'started_at' not in ds:
    #    import epdb; epdb.st()
    logger.info(ds['started_at'] + ' > ' + ds['finished_at'])

    # 2022-07-26T17:34:53.416884-04:00
    ts0 = ds['started_at'].split('.')[0]
    ts0 = datetime.datetime.strptime(ts0, '%Y-%m-%dT%H:%M:%S')
    tsN = ds['finished_at'].split('.')[0]
    tsN = datetime.datetime.strptime(tsN, '%Y-%m-%dT%H:%M:%S')
    delta = (tsN - ts0).total_seconds()
    durations.append([delta, tf])

#durations = sorted(durations)
for duration in durations[::-1]:
    this_import = imports[duration[1]]
    fqcn = f"{this_import['namespace']['name']}.{this_import['name']}"
    fqcnv = f"{this_import['namespace']['name']}.{this_import['name']}.{this_import['version']}"

    if 'cisco.ios' not in fqcn:
        continue

    logger.info(f"{this_import['job_id']} {this_import['started_at']} {duration[0]} {fqcnv}")

    if 'error' in this_import and this_import.get('error'):
        logger.error(this_import['error']['description'])

    if this_import['job_id'].startswith('def0'):
        logger.error('#' * 50)
        #import epdb; epdb.st()

import epdb; epdb.st()


collections = []
next_url = BASEURL + '/api/v2/collections'
while next_url:
    res = get_cached_url(next_url, logger=logger)
    ds = json.loads(res.data)

    collections.extend(ds['results'])

    if ds['next'] is None:
        break
    next_url = BASEURL + ds['next']


collections = sorted(collections, key=lambda x: x['modified'], reverse=True)
for col in collections:
    cversion_urls = []
    next_url = col['versions_url']
    while next_url:
        res = get_cached_url(next_url, logger=logger)
        ds = json.loads(res.data)
        cversion_urls.extend([x['href'] for x in ds['results']])
        if ds['next'] is None:
            break
        next_url = ds['next']
    for cvurl in cversion_urls:
        res = get_cached_url(cvurl, logger=logger)
        ds = json.loads(res.data)
        import epdb; epdb.st()

import epdb; epdb.st()


next_url = BASEURL + '/api/v1/roles'
while next_url:
    logger.info(next_url)
    res = get_cached_url(next_url, logger=logger)

    ise = False
    try:
        json.loads(res.data)
    except Exception as e:
        ise = True

    if not ise and res.data is None:
        ise = True

    if ise:
        if '=' not in next_url:
            pagenum = 1
            next_url = BASEURL + '/api/v1/roles/?page=' + str(pagenum)
        else:
            pagenum = int(next_url.split('=')[-1]) + 1
            next_url = next_url.split('=')[0] + '=' + str(pagenum)
        logger.error('FOUND ISE, CONTINUING')
        continue

    ds = json.loads(res.data)
    if 'next' not in ds:
        logger.error('NO NEXT, BREAKING')
        break

    if ds['next']:
        next_url = BASEURL + '/api/v1' + ds['next']
    else:
        next_url = None

    for role in ds['results']:
        role_url = BASEURL + role['url']

        # versions ...
        next_role_versions_url = role_url + 'versions/'
        while next_role_versions_url:
            rvs = get_cached_url(next_role_versions_url, logger=logger)
            rvs = json.loads(rvs.data)
            next_role_versions_url = None
            if rvs['next']:
                next_role_versions_url = BASEURL + '/api/v1' + rvs['next']

        '''
        # related ...
        next_related_url = role_url + 'related/'
        while next_related_url:
            print(next_related_url)
            rrr = get_cached_url(next_related_url, logger=logger)
            import epdb; epdb.st()
        '''

        # dependencies ...
        next_deps_url = role_url + 'dependencies/'
        while next_deps_url:
            rrd = get_cached_url(next_deps_url, logger=logger)
            try:
                deps = json.loads(rrd.data)
            except json.decoder.JSONDecodeError:
                import epdb; epdb.st()
            if 'next' not in deps:
                import epdb; epdb.st()
            if deps['next']:
                next_deps_url = BASEURL + '/api/v1' + deps['next']
                continue
            break


next_url = BASEURL + '/api/v2/collections'
while next_url:
    logger.info(next_url)
    res = get_cached_url(next_url, logger=logger)
    ds = json.loads(res.data)
    import epdb; epdb.st()
