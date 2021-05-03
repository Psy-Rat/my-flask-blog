from flask import render_template, request

from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name

import misaka as m
import houdini as h

import flask_misaka


def render_paginated(template_name, query, paginate_by=20, **context):
    '''
        Paginate query by flask. Returns rendered template with items after pagination.

    '''
    page = request.args.get('page')

    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    object_list = query.paginate(page, paginate_by)

    return render_template(
        template_name,
        object_list=object_list,
        **context)


class HighlighterRenderer(m.HtmlRenderer):
    def __init__(self, *args, **kwargs):

        self.formatter = HtmlFormatter(
            cssclass="code-block", style='monokai', full=False, linenos='table')

        super(HighlighterRenderer, self).__init__(*args, **kwargs)

    def get_styles(self):
        return f"<style type=\"text/css\">{self.formatter.get_style_defs()}</style>"

    def blockcode(self, text, lang):
        print(lang)
        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except ClassNotFound:
            lexer = None

        if lexer:
            # style_defs = formatter.get_style_defs()
            return f"{highlight(text, lexer, self.formatter)}\n"
        # default
        print("USES DEFAULT LEXER")
        return f"\n<div class=\"code-block-{lang}\"><pre><code>{h.escape_html(text)}</code></pre></div>\n"

    def header(self, content, level):
        return f"<a name = \"{content}\"><h{level}>{content}</h{level}></a>"


renderer = HighlighterRenderer()


def markdown(text_md, **options):
    '''
    Renders markdown text to html


    Parameters:
        text_md (str): Text in markdown
        **options: https://flask-misaka.readthedocs.io/en/latest/#options
    '''
    return flask_misaka.markdown(text_md, renderer=renderer, **options)
