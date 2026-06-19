#!/usr/bin/env python3
"""Serve the frontend directory on localhost and open the browser."""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import argparse
import threading

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8001)
args = parser.parse_args()

ROOT = Path(__file__).resolve().parents[1] / 'frontend'

class _Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

def run():
    with socketserver.TCPServer(('127.0.0.1', args.port), _Handler) as httpd:
        url = f'http://127.0.0.1:{args.port}/'
        print('Serving frontend at', url)
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Stopping server')

if __name__ == '__main__':
    run()
