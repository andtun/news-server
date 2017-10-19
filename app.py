# This Python file uses the following encoding: utf-8

import os
from bottle import *


@get("/")
def main():
    return static_file("index.html", root='.')

# run the server
run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
