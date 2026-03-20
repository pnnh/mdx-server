import re
from html import escape

def raw_mdx_to_nice_html(raw: str, remove_injection: bool = True) -> str:
    """
    将老版 MDX 原始记录转换为带响应式内联样式的美观 HTML。
    优化重点：小屏幕（手机）阅读体验优先。
    """
    text = raw.strip()

    # 移除尾部注入脚本
    if remove_injection:
        text = re.split(
            r'(?is)<link\s+rel="stylesheet".*?injection\.css.*?</script>\s*$',
            text
        )[0]

    text = re.sub(r'(?i)</br\s*>', '<br>', text)

    replacements = [
        (r'`1`([^`]+)`2`', r'<h2 class="headword">\1</h2>'),
        (r'`3`([^`]+)`4`', r'<div class="phonetic">\1</div>'),
        (r'-([A-Z]\d)', r'<sup class="pron-variant">\1</sup>'),
        (r'`2`{2,}', '</p>\n<p class="def-block">'),
        (r'`2`', '</p>\n<p class="def-block">'),
        (r'`5`', '<span class="example-label">例</span> '),
        (r'`6`', '<span class="colloc-label">搭配</span> '),
        (r'`7`', '<span class="syn-label">同</span> '),
        (r'(?m)^([a-z]{1,4}\.)\s', r'<strong class="pos">\1</strong> '),
    ]

    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)

    text = re.sub(r'<p class="def-block">\s*</p>', '', text)
    text = re.sub(r'\n\s*\n+', '\n', text)

    # ────────────────────────────────────────────────
    # 响应式内联 CSS（mobile-first）
    # ────────────────────────────────────────────────
    css = """
    <style>
        .mdx-entry {
            font-family: system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
            line-height: 1.65;
            color: #1f2937;
            margin: 0;
            padding: 1rem 0.9rem;
            background: #ffffff;
            font-size: 15px;          /* 小屏基础字号 */
            -webkit-text-size-adjust: 100%;
            text-size-adjust: 100%;
            word-break: break-all;     /* 中英文混合时防溢出 */
            hyphens: auto;
            overflow-wrap: break-word;
        }

        .headword {
            font-size: clamp(1.6rem, 7.5vw, 2.1rem);
            font-weight: 700;
            color: #1e40af;
            margin: 0.5rem 0 0.8rem;
            line-height: 1.2;
            letter-spacing: -0.01em;
        }

        .phonetic {
            font-size: clamp(1rem, 4.8vw, 1.25rem);
            color: #4b5563;
            font-family: "Lucida Sans Unicode", "DejaVu Sans", Consolas, monospace;
            margin: 0.4rem 0 1.1rem;
            background: #f3f4f6;
            padding: 0.4rem 0.75rem;
            border-radius: 0.35rem;
            display: inline-block;
            line-height: 1.4;
        }

        .pron-variant {
            font-size: 0.72em;
            color: #6b7280;
            vertical-align: super;
        }

        .pos {
            color: #4338ca;
            font-weight: 600;
            margin-right: 0.45em;
        }

        .def-block {
            margin: 1rem 0;
            padding-left: 0.9rem;
            border-left: 3px solid #cbd5e1;
            font-size: 1em;
        }

        .def-block:first-of-type {
            margin-top: 0.6rem;
        }

        .example-label,
        .colloc-label,
        .syn-label {
            font-size: 0.78rem;
            color: #64748b;
            background: #e2e8f0;
            padding: 0.12rem 0.38rem;
            border-radius: 0.22rem;
            margin-right: 0.45rem;
            vertical-align: middle;
        }

        br {
            content: "";
            display: block;
            margin: 0.7em 0;
        }

        /* ─── 大屏幕增强 ────────────────────────────────────── */
        @media (min-width: 520px) {
            .mdx-entry {
                padding: 1.4rem 1.2rem;
                border-radius: 0.6rem;
                box-shadow: 0 3px 12px rgba(0,0,0,0.07);
                margin: 0.8rem auto;
                max-width: 820px;
                font-size: 16px;
            }

            .def-block {
                padding-left: 1.2rem;
                margin: 1.2rem 0;
            }

            .phonetic {
                padding: 0.45rem 1rem;
            }
        }

        @media (min-width: 768px) {
            .mdx-entry {
                font-size: 17px;
                padding: 1.6rem 2rem;
            }

            .headword {
                font-size: clamp(2.1rem, 5vw, 2.6rem);
            }
        }

        /* 深色模式（可选，根据实际环境开启） */
        @media (prefers-color-scheme: dark) {
            .mdx-entry {
                background: #111827;
                color: #e5e7eb;
            }
            .headword { color: #60a5fa; }
            .phonetic { background: #1f2937; color: #9ca3af; }
            .def-block { border-left-color: #4b5563; }
            .pos { color: #818cf8; }
            .example-label, .colloc-label, .syn-label {
                background: #334155;
                color: #cbd5e1;
            }
        }
    </style>
    """

    html = f'{css}<div class="mdx-entry">\n{text}\n</div>'

    return html