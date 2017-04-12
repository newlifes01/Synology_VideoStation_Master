#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import threading

import os

import utils
import logging

try:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
except ImportError:
    from http.server import SimpleHTTPRequestHandler

try:
    from SocketServer import TCPServer as HTTPServer
except ImportError:
    from http.server import HTTPServer

class HttpServer:
    def __init__(self, port):
        self.httpd = None
        self.httpserver_thread = threading.Thread(target=self.start_thread, name='HttpThread', args=(port,),
                                                  daemon=True)
        self.httpserver_thread.start()
        self.logger = logging.getLogger('HttpServer')

    def __del__(self):
        if self.httpd:
            self.httpd.server_close()

    def start_thread(self, port):
        old_path = os.getcwd()
        if not os.path.exists(utils.CACHE_PATH):
            os.mkdir(utils.CACHE_PATH)

        web_dir = utils.CACHE_PATH
        os.chdir(web_dir)

        self.httpd = HTTPServer(("", port), SimpleHTTPRequestHandler)
        utils.add_log(self.logger,'info',"serving at port {0}".format(port))
        self.httpd.serve_forever()

        os.chdir(old_path)
