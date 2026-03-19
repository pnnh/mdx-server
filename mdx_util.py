# -*- coding: utf-8 -*-
# version: python 3.5

import sys
import re
import subprocess
from file_util import *

def get_definition_mdx(word, builder):
    """根据关键字得到MDX词典的解释"""
    # Only use the first line — callers may pass multi-line selected text
    word = word.split('\n')[0].strip()
    content = builder.mdx_lookup(word)
    if len(content) < 1:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        proc = subprocess.run(
            [sys.executable, os.path.join(script_dir, 'lemma.py'), word],
            capture_output=True, text=True
        )
        word = proc.stdout.strip()
        print("lemma: " + word)
        if word:
            content = builder.mdx_lookup(word)
    pattern = re.compile(r"@@@LINK=([\w\s]*)")
    if len(content) < 1:
        return [b'']
    rst = pattern.match(content[0])
    if rst is not None:
        link = rst.group(1).strip()
        content = builder.mdx_lookup(link)
    str_content = ""
    if len(content) > 0:
        for c in content:
            str_content += c.replace("\r\n","").replace("entry:/","")

    injection = []
    injection_html = ''
    output_html = ''

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
            
    resource_path = os.path.join(base_path, 'mdx')

    file_util_get_files(resource_path, injection)

    for p in injection:
        if file_util_is_ext(p, 'html'):
            injection_html += file_util_read_text(p)

    #return [bytes(str_content, encoding='utf-8')]
    output_html = str_content + injection_html
    return [output_html.encode('utf-8')]

def get_definition_mdd(word, builder):
    """根据关键字得到MDX词典的媒体"""
    word = word.replace("/","\\")
    if not hasattr(builder, '_mdd_db'):
        return []
    content = builder.mdd_lookup(word)
    if len(content) > 0:
        return [content[0]]
    else:
        return []
