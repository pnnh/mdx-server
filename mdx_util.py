# -*- coding: utf-8 -*-
# version: python 3.5

import sys
import re
import subprocess
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'html'))
from nice_html import raw_mdx_to_nice_html
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
            str_content += c.replace("\r\n", "").replace("entry:/", "")

    output_html = raw_mdx_to_nice_html(str_content)
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
