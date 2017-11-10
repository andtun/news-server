# This Python file uses the following encoding: utf-8

import os
from bottle import *


def html(filename):
    return static_file(filename+".html", root='.')


@get("/")
def main():
    return html("main")


# ==================== Get template files ===================

@get("/<filename>")
def get_it(filename):
    return static_file(filename, root='.')


@get("/<whatever>/<filename>")
def get_it(whatever, filename):
    return static_file(filename, root=whatever)


@get("/<whatever>/<wherever>/<filename>")
def get_it(whatever, wherever, filename):
    return static_file(filename, root=whatever+"/"+wherever)


# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
