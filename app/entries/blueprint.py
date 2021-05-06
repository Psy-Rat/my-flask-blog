from flask import Blueprint, render_template, redirect, url_for, request
from helpers import entry_list_search, markdown, get_anchors, parse_anchors_as_bootstrap
from models import Entry, Tag
from collections import namedtuple
from entries.forms import EntryForm
from app import db

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


# Creation model
def create_entry_post():
    form = EntryForm(request.form)
    if form.validate():
        entry = form.save_entry(Entry())
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        return render_template('entries/create.html', form=form)


@entries.route('/create/', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        return create_entry_post()
    elif request.method == 'GET':
        form = EntryForm()
        return render_template('entries/create.html', form=form)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"


@entries.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug == slug).first_or_404()
    anchors = get_anchors(entry.body)
    main_data = markdown(
        entry.body, anchors, math=True, fenced_code=True)
    anch = parse_anchors_as_bootstrap(
        anchors)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data, scrollspy=anch)

# Edit model


def entry_edit_post_responce(entry):
    # obj param help to autofill form from entry by comparing attributes
    form = EntryForm(request.form, obj=entry)
    if form.validate():
        entry = form.save_entry(entry)
        db.session.add(entry)
        db.session.commit()
        return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        return render_template('entries/edit.html', entry=entry, form=form)


def entry_edit_get_responce(entry):
    form = EntryForm(obj=entry)
    return render_template('entries/edit.html', entry=entry, form=form)


@entries.route('/<slug>/edit', methods=['GET', 'POST'])
def edit(slug):
    entry = Entry.query.filter(Entry.slug == slug).first_or_404()
    if request.method == 'POST':
        return entry_edit_post_responce(entry)
    elif request.method == 'GET':
        return entry_edit_get_responce(entry)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"
