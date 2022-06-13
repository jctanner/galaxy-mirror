#!/usr/bin/env python

import json
import hashlib
import os

from flask import jsonify
from flask import Flask
from flask import redirect
from flask import request
from flask import Response

import requests


app = Flask(__name__)

BASEURL = 'https://galaxy.ansible.com'
CACHEDIR = '/data'


def get_cached_url(url):
    ho = hashlib.sha256(url.encode('utf-8'))
    hd = ho.hexdigest()
    _cd = os.path.join(CACHEDIR, hd[:3])
    if not os.path.exists(_cd):
        os.makedirs(_cd)
    cf = f'{_cd}/{hd}.json'

    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)

    if not os.path.exists(cf):
        app.logger.info(f'CACHE MISS {url}')

        rr = requests.get(url)
        mimetype = 'application/json'
        try:
            ds = rr.json()
        except Exception as e:
            mimetype = 'applicaiton/text'

        with open(cf, 'w') as f:
            f.write(json.dumps({
                'headers': dict(rr.headers),
                'status_code': rr.status_code,
                'mimetype': mimetype,
                'text': rr.text,
                'url': url,
                #'data': ds
            }, indent=2))

        return Response(rr.text, status=rr.status_code, mimetype='application/json')

    app.logger.info(f'CACHE HIT {url}')
    with open(cf, 'r') as f:
        ds = json.loads(f.read())
    return Response(ds['text'], status=ds['status_code'], mimetype=ds['mimetype'])


@app.route('/')
def root():
    return redirect('/api/')


@app.route('/api/')
def api_root():
    this_url = BASEURL + '/api/'
    return get_cached_url(this_url)
    if ds:
        return jsonify(ds), code
    return text, code


@app.route('/api/<path:api_path>')
def api_abstract_path(api_path):
    this_url = BASEURL + '/api/' + api_path
    if request.args:
        this_url += '?'
        keys = sorted(list(dict(request.args).keys()))
        for k in keys:
            v= dict(request.args)[k]
            this_url += f'{k}={v}'
    return get_cached_url(this_url)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
