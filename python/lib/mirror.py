#!/usr/bin/env python

import json
import hashlib
import os

import requests
from flask import Response


BASEURL = 'https://galaxy.ansible.com'
CACHEDIR = '/data'


def get_cached_url(url, logger=None, token=None, refresh=False):
    ho = hashlib.sha256(url.encode('utf-8'))
    hd = ho.hexdigest()
    _cd = os.path.join(CACHEDIR, hd[:3])
    if not os.path.exists(_cd):
        os.makedirs(_cd)
    cf = f'{_cd}/{hd}.json'

    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)

    if not os.path.exists(cf) or refresh:
        if logger:
            logger.info(f'CACHE MISS {url}')

        headers = {}
        if token is not None:
            headers['Authorization'] = f'token {token}'

        rr = requests.get(url, headers=headers)
        mimetype = 'application/json'
        try:
            ds = rr.json()
        except Exception as e:
            mimetype = 'application/text'

        with open(cf, 'w') as f:
            f.write(json.dumps({
                'headers': dict(rr.headers),
                'status_code': rr.status_code,
                'mimetype': mimetype,
                'text': rr.text,
                'url': url,
                #'data': ds
            }, indent=2))

        return Response(rr.text, status=rr.status_code, mimetype=mimetype)

    if logger:
        logger.info(f'CACHE HIT {url}')

    with open(cf, 'r') as f:
        ds = json.loads(f.read())

    if ds['mimetype'] != 'applicaton/json':
        ds['mimetype'] = 'application/text'

    return Response(ds['text'], status=ds['status_code'], mimetype=ds['mimetype'])
