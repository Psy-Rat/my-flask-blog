from flask import Blueprint, render_template
from helpers import render_paginated, markdown, get_anchors, parse_anchors_as_bootstrap
from models import Entry, Tag

entries = Blueprint(
    'entries',
    __name__,
    template_folder='templates')


@entries.route('/')
def index():
    entries = Entry.query.order_by(Entry.created_timestamp.desc())
    print(entries)
    return render_paginated('entries/index.html', entries)


@entries.route('/tags/')
def tag_index():
    tags = Tag.query.order_by(Tag.name)
    return render_paginated('entries/index_tag.html', tags)


@entries.route('/tags/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    entries = tag.entries.order_by(Entry.created_timestamp.desc())
    return render_paginated('entries/detail_tag.html', entries, tag=tag)


@entries.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug == slug).first_or_404()
    anchors = get_anchors(entry.body)
    main_data = markdown(
        entry.body, anchors, math=True, fenced_code=True)
    anch = parse_anchors_as_bootstrap(
        anchors)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data, scrollspy=anch)
