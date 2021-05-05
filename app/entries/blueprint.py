from flask import Blueprint, render_template
from helpers import entry_list_search, markdown, get_anchors, parse_anchors_as_bootstrap
from models import Entry, Tag
from collections import namedtuple


DummyTag = namedtuple("DummyTag", ["name"])


entries = Blueprint(
    'entries',
    __name__,
    template_folder='templates')


@entries.route('/')
def index():
    entries = Entry.query.order_by(Entry.created_timestamp.desc())
    print(entries)
    return entry_list_search('entries/index.html', entries)


@entries.route('/tags/')
def tag_index():
    tags = Tag.query.order_by(Tag.name)
    return entry_list_search('entries/index_tag.html', tags)


def single_tag_search(slug):
    tag = Tag.query.filter(Tag.slug == slug).first_or_404()
    entries = tag.entries.order_by(Entry.created_timestamp.desc())
    return entry_list_search('entries/detail_tag.html', entries, tag=tag)


def multiple_tag_search(slug_list):
    ''' ToDo: rewrite completely
    '''
    query_filter = Tag.slug == ""
    f_empty = False
    for slug in slug_list:
        query_filter |= Tag.slug == slug
        if Tag.query.filter(Tag.slug == slug).count() == 0:
            return render_template('entries/detail_tag.html',
                                   object_list=None,
                                   tag=[DummyTag(name=slug) for slug in slug_list])

    tags = Tag.query.filter(query_filter).all()
    q_entries = [tag.entries for tag in tags]
    entries = q_entries[0].intersect(
        *q_entries[1:]).order_by(Entry.created_timestamp.desc())

    return entry_list_search('entries/detail_tag.html', entries, tag=tags)


@entries.route('/tags/<slug>/')
def tag_detail(slug):
    slug_list = slug.split('+')
    if len(slug_list) == 1:
        return single_tag_search(slug)
    else:
        return multiple_tag_search(slug_list)


@entries.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug == slug).first_or_404()
    anchors = get_anchors(entry.body)
    main_data = markdown(
        entry.body, anchors, math=True, fenced_code=True)
    anch = parse_anchors_as_bootstrap(
        anchors)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data, scrollspy=anch)
