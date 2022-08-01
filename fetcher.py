#!/usr/bin/env python3

from logzero import logger

from lib.mirror import get_cached_url
from lib.mirror import BASEURL

next_url = BASEURL + '/api/v1/roles'

while next_url:
    print(next_url)
    res = get_cached_url(next_url, logger=logger)

    ise = False
    try:
        res.json
    except Exception as e:
        ise = True

    if not ise and res.json is None:
        ise = True

    if ise:
        if '=' not in next_url:
            pagenum = 1
            next_url = BASEURL + '/api/v1/roles/?page=' + str(pagenum)
        else:
            pagenum = int(next_url.split('=')[-1]) + 1
            next_url = next_url.split('=')[0] + '=' + str(pagenum)
        continue

    if 'next' not in res.json:
        break

    if res.json['next']:
        next_url = BASEURL + '/api/v1' + res.json['next']
    else:
        next_url = None

    for role in res.json['results']:
        role_url = BASEURL + role['url']
        next_role_versions_url = role_url + 'versions/'
        while next_role_versions_url:
            print(next_role_versions_url)
            rvs = get_cached_url(next_role_versions_url, logger=logger)
            if rvs is None:
                import epdb; epdb.st()
            next_role_versions_url = None
            if rvs.json['next']:
                next_role_versions_url = BASEURL + '/api/v1' + rvs.json['next']
