#!/usr/bin/env python

import json
import hashlib
import os

from flask import jsonify
from flask import Flask
from flask import redirect
from flask import request
from flask import Response

from lib.mirror import get_cached_url
from lib.mirror import BASEURL


app = Flask(__name__)


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
