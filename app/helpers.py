from flask import render_template, request

from pygments import highlight
from pygments.formatters import HtmlFormatter, ClassNotFound
from pygments.lexers import get_lexer_by_name

import misaka as m
import houdini as h

import flask_misaka

from copy import deepcopy
import re

from models import Entry


def render_paginated(template_name, query, paginate_by=10, **context):
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
        self.had_gen = []
        self.formatter = HtmlFormatter(
            cssclass="code-block", style='monokai', full=False, linenos='table')

        super(HighlighterRenderer, self).__init__(*args, **kwargs)

    def set_anchors(self, had_container):
        self.had_gen = list(had_container.generator_forward())
        self.had_gen.reverse()

    def get_styles(self):
        return f"<style type=\"text/css\">{self.formatter.get_style_defs()}</style>"

    def blockcode(self, text, lang):
        # print(lang)
        try:
            lexer = get_lexer_by_name(lang, stripall=False)
        except ClassNotFound:
            lexer = None

        if lexer:
            # style_defs = formatter.get_style_defs()
            return f"{highlight(text, lexer, self.formatter)}\n"
        # default
        # print("USES DEFAULT LEXER")
        return f"\n<div class=\"code-block-{lang}\"><pre><code>{h.escape_html(text)}</code></pre></div>\n"

    def header(self, content, level):
        if len(self.had_gen) > 0:
            # print("AHAHAHAHAH")
            id_ref = self.had_gen.pop().slug
            link = f"<a class = \"inline-anchor\" href=\"#{id_ref}\"><i>&para;</i></a>"
            return f"<h{level} id=\"{id_ref}\" class = \"entity-header\">{link}{content}</h{level}>"
        else:
            return f"<h{level} class = \"entity-header\">{content}</h{level}>"


renderer = HighlighterRenderer()


def markdown(text_md, had_gen=None, **options):
    '''
    Renders markdown text to html


    Parameters:
        text_md (str): Text in markdown
        **options: https://flask-misaka.readthedocs.io/en/latest/#options
    '''
    renderer.set_anchors(had_gen)
    return flask_misaka.markdown(text_md, renderer=renderer, **options)


class HeaderAnchorData():
    def __init__(self, content, level, unique_set=None):
        self.content = content
        self.level = level
        self.slug = self.slugify(content, unique_set)

    def slugify(self, text, unique_set=None):
        slug = re.sub('[^\w]+', '-', text).lower()
        if unique_set is None:
            return slug
        else:
            return self.change_till_unique(slug, unique_set)

    def change_till_unique(self, text, unique_set, number=1):
        if text not in unique_set:
            return text

        while True:
            test_text = f"{text}-{number}"
            if test_text in unique_set:
                number += 1
                continue
            else:
                return test_text

    def __repr__(self):
        return f"<{self.content} [{self.level}] [[{self.slug}]]>"

    def copy(self):
        copy = HeaderAnchorData(self.content, self.level)
        copy.slug = self.slug
        return copy


class HeaderRenderer(m.BaseRenderer):
    def __init__(self, *args, **kwargs):
        self.memory = []
        self.slugs_set = set()
        super(HeaderRenderer, self).__init__(*args, **kwargs)

    def flush(self):
        self.memory = []
        self.slugs_set = set()

    def doc_header(self, inline_render):
        self.flush()
        print("start?")

    def doc_footer(self, inline_render):
        print("fin?")

    def header(self, content, level):
        # print(content, level)
        print(self.slugs_set)
        head_data = HeaderAnchorData(content, level, self.slugs_set)
        self.memory.append(head_data)
        self.slugs_set.add(head_data.slug)
        return f"<h{level}>{content}</h{level}>"


class HeaderAnchorDataContainer:
    def __init__(self, had_list):
        self.had_list = deepcopy(had_list)
        if len(had_list) > 0:
            self.low_pass = min(self.had_list, key=lambda x: x.level).level
        else:
            self.low_pass = 0

    def generator_forward(self, relative=False):
        if not relative:
            return (x for x in self.had_list)
        else:
            def filtration():
                for had in self.had_list:
                    res = had.copy()
                    res.level = res.level - self.low_pass
                    yield res
            return filtration()


class HeaderAnchorBootstrapRenderer:

    NAVb = "<nav class=\"nav nav-pills flex-column\">"
    NAVe = "</nav>"
    MARGIN_CLASS = "pl-"
    LINK_CLASS = "nav-link softscroll"

    def construct_nav(self, id):
        return f"<nav id=\"{id}\" class=\"container\">"

    def construct_link(self, level, href, content):
        LINK_BEG = f"<a class=\"{self.LINK_CLASS} {self.MARGIN_CLASS}{level}\" "
        HREF = f"href=\"{href}\">"
        LINK_END = f"{content}</a>"
        return LINK_BEG + HREF + LINK_END

    def parse(self, had_container: HeaderAnchorDataContainer, id="navbar-scrollspy"):
        curr_level = 0
        parse_res = ""

        def start_nav():
            nonlocal parse_res
            nonlocal curr_level
            parse_res = parse_res + self.construct_nav(id)

        def add_layer():
            nonlocal parse_res
            nonlocal curr_level
            curr_level += 1
            parse_res = parse_res + "\n" + self.NAVb

        def layer_return():
            nonlocal parse_res
            nonlocal curr_level
            curr_level -= 1
            parse_res = parse_res + "\n" + self.NAVe

        def add_link(had):
            nonlocal parse_res
            nonlocal curr_level
            link = self.construct_link(curr_level, f"#{had.slug}", had.content)
            parse_res = parse_res + "\n" + "  " * curr_level + link

        had_gen = had_container.generator_forward(relative=True)
        print(had_gen)

        # start_nav()

        for had in had_gen:
            while curr_level < had.level:
                add_layer()
            while curr_level > had.level:
                layer_return()

            add_link(had)

        while curr_level > -1:
            layer_return()

        return parse_res


head_ren = HeaderRenderer()
had_parser = HeaderAnchorBootstrapRenderer()


def get_anchors(text):
    flask_misaka.markdown(text, head_ren)
    had_cnt = HeaderAnchorDataContainer(head_ren.memory)
    return had_cnt


def parse_anchors_as_bootstrap(anchors):
    return had_parser.parse(anchors)


def entry_list_search(template, query, **context):
    search = request.args.get('q')
    if search:
        query = query.filter(
            (Entry.body.contains(search)) | (Entry.title.contains(search)))
    return render_paginated(template, query, **context)
