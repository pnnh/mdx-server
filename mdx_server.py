# -*- coding: utf-8 -*-
# version: python 3.5

import threading
import re
import os
import sys


if sys.version_info < (3, 0, 0):
    import Tkinter as tk
    import tkFileDialog as filedialog
else:
    import tkinter as tk
    import tkinter.filedialog as filedialog

from wsgiref.simple_server import make_server
from file_util import *
from mdx_util import *
from mdict_query import IndexBuilder

"""
browser URL:
http://localhost:8000/test
"""

content_type_map = {
    'html': 'text/html; charset=utf-8',
    'js': 'application/x-javascript',
    'ico': 'image/x-icon',
    'css': 'text/css',
    'jpg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'mp3': 'audio/mpeg',
    'mp4': 'audio/mp4',
    'wav': 'audio/wav',
    'spx': 'audio/ogg',
    'ogg': 'audio/ogg',
    'eot': 'font/opentype',
    'svg': 'text/xml',
    'ttf': 'application/x-font-ttf',
    'woff': 'application/x-font-woff',
    'woff2': 'application/font-woff2',
}

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except AttributeError:
    base_path = os.path.dirname(os.path.abspath(__file__))
        
resource_path = os.path.join(base_path, 'mdx')
print("resouce path : " + resource_path)
builder = None


def get_url_map():
    result = {}
    files = []

    # resource_path = '/mdx'
    file_util_get_files(resource_path, files)
    for p in files:
        if file_util_get_ext(p) in content_type_map:
            p = p.replace('\\', '/')
            result[re.match('.*?/mdx(/.*)', p).groups()[0]] = p
    return result


def application(environ, start_response):
    path_info = environ['PATH_INFO'].encode('iso8859-1').decode('utf-8')
    query_string = environ.get('QUERY_STRING', '')
    print(path_info + ('?' + query_string if query_string else ''))

    # ── 1. Built-in mdx/ injection assets (highest priority) ──────────────
    url_map = get_url_map()
    if path_info in url_map:
        url_file = url_map[path_info]
        content_type = content_type_map.get(file_util_get_ext(url_file), 'text/html; charset=utf-8')
        start_response('200 OK', [('Content-Type', content_type)])
        return [file_util_read_byte(url_file)]

    # ── 2. content/public/ static files ───────────────────────────────────
    public_dir = os.path.join(os.getcwd(), 'content', 'public')
    if os.path.isdir(public_dir):
        # strip leading slash, prevent path traversal
        rel = os.path.normpath(path_info.lstrip('/'))
        if not rel.startswith('..'):
            candidate = os.path.join(public_dir, rel)
            if os.path.isfile(candidate):
                content_type = content_type_map.get(file_util_get_ext(candidate), 'application/octet-stream')
                start_response('200 OK', [('Content-Type', content_type)])
                return [file_util_read_byte(candidate)]

    # ── 3. MDD media lookup (legacy /{path.ext} pattern) ──────────────────
    if file_util_get_ext(path_info) in content_type_map:
        content_type = content_type_map.get(file_util_get_ext(path_info), 'text/html; charset=utf-8')
        start_response('200 OK', [('Content-Type', content_type)])
        return get_definition_mdd(path_info, builder)

    # ── 4. Word lookup  /?word=<word> ──────────────────────────────────────
    from urllib.parse import parse_qs
    params = parse_qs(query_string)
    word_list = params.get('word', [])
    if word_list:
        word = word_list[0]
        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        return get_definition_mdx(word, builder)

    start_response('400 Bad Request', [('Content-Type', 'text/plain; charset=utf-8')])
    return [b'Missing required query parameter: word']


# 新线程执行的代码
def loop():
    # 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
    httpd = make_server('', 8000, application)
    print("Serving HTTP on port 8000...")
    # 开始监听HTTP请求:
    httpd.serve_forever()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs='?', help="mdx file name")
    args = parser.parse_args()

    # auto-detect *.mdx under ./content/ before falling back to GUI
    if not args.filename:
        content_dir = os.path.join(os.getcwd(), 'content')
        if os.path.isdir(content_dir):
            mdx_files = sorted(
                p for root, _, files in os.walk(content_dir)
                for f in files if f.lower().endswith('.mdx')
                for p in [os.path.join(root, f)]
            )
            if mdx_files:
                args.filename = mdx_files[0]
                print("Auto-detected MDX file: " + args.filename)

    # use GUI to select file, default to extract
    if not args.filename:
        if sys.platform == 'darwin':
            # macOS: use native AppleScript dialog to avoid Tkinter window positioning
            # and event loop issues when running as a non-bundle Python script
            import subprocess
            script = 'POSIX path of (choose file with prompt "Select MDX/MDD File:")'
            proc = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            args.filename = proc.stdout.strip() if proc.returncode == 0 else ''
        else:
            root = tk.Tk()
            root.withdraw()
            root.update()
            args.filename = filedialog.askopenfilename(
                parent=root,
                title='Select MDX/MDD File',
                filetypes=[('MDict files', '*.mdx *.mdd'), ('All files', '*.*')]
            )
            root.destroy()

    if not os.path.exists(args.filename):
        print("Please specify a valid MDX/MDD file")
    else:
        builder = IndexBuilder(args.filename)
        t = threading.Thread(target=loop, args=())
        t.start()
