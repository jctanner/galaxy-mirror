#!/usr/bin/env python

from flask import jsonify
from flask import Flask
from flask import redirect

import requests
import requests_cache


app = Flask(__name__)

BASEURL = 'https://galaxy.ansible.com'
requests_cache.install_cache('/data/demo_cache')


@app.route('/')
def root():
    return redirect('/api/')


@app.route('/api/')
def api_root():
    rr = requests.get(BASEURL + '/api/')
    return jsonify(rr.json())


@app.route('/api/<path:api_path>')
def api_abstract_path(api_path):
    this_url = BASEURL + '/api/' + api_path
    print(f'GET {this_url}')
    rr = requests.get(this_url)
    return jsonify(rr.json())


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
