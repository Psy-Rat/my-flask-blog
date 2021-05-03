from flask import Blueprint, render_template
from helpers import render_paginated, markdown
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
    pass


@entries.route('/tags/<slug>/')
def tag_detail(slug):
    tag = Tag.query.filter(Tag)
    pass


@entries.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug == slug).first_or_404()
    main_data = markdown(entry.body, math=True, fenced_code=True)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data)
