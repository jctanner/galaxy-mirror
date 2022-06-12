#!/usr/bin/env python

import json
import hashlib
import os

from flask import jsonify
from flask import Flask
from flask import redirect
from flask import request

import requests
#import requests_cache


app = Flask(__name__)

BASEURL = 'https://galaxy.ansible.com'
CACHEDIR = '/data'
#requests_cache.install_cache('/data/demo_cache')


def get_cached_url(url):
    ho = hashlib.sha256(url.encode('utf-8'))
    hd = ho.hexdigest()
    cf = f'{CACHEDIR}/{hd}.json'

    if not os.path.exists(CACHEDIR):
        os.makedirs(CACHEDIR)

    if not os.path.exists(cf):
        app.logger.info(f'CACHE MISS {url}')

        rr = requests.get(url)
        ds = rr.json()
        with open(cf, 'w') as f:
            f.write(json.dumps({'url': url, 'data': ds}, indent=2))

        return ds

    app.logger.info(f'CACHE HIT {url}')
    with open(cf, 'r') as f:
        return json.loads(f.read())['data']


@app.route('/')
def root():
    return redirect('/api/')


@app.route('/api/')
def api_root():
    this_url = BASEURL + '/api/'
    #print(f'GET {this_url}')
    #rr = requests.get(this_url)
    #return jsonify(rr.json())
    return get_cached_url(this_url)


@app.route('/api/<path:api_path>')
def api_abstract_path(api_path):
    this_url = BASEURL + '/api/' + api_path
    if request.args:
        this_url += '?'
        for k,v in dict(request.args).items():
            this_url += f'{k}={v}'
    #print(f'GET {this_url}')
    #rr = requests.get(this_url)
    #return jsonify(rr.json())
    return get_cached_url(this_url)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
