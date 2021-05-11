from flask import Blueprint, flash, render_template, redirect, url_for, request
from collections import namedtuple

from .forms import EntryForm
from ...helpers import entry_list_search, markdown, get_anchors, parse_anchors_as_bootstrap
from ...models import Entry, Tag

from ...services.entry import EntryService

from ...app import db

DummyTag = namedtuple("DummyTag", ["name"])


entries = Blueprint(
    'entries',
    __name__,
    template_folder='templates')


@entries.route('/')
def index():
    entries = EntryService.get_entries_ordered_by_date()
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
        flash(f'Статья «{entry.title} создана»', 'success')
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
    entry = EntryService.get_entry_or_404(slug)
    anchors = get_anchors(entry.body)
    main_data = markdown(
        entry.body, anchors, math=True, fenced_code=True)
    anch = parse_anchors_as_bootstrap(
        anchors)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data, scrollspy=anch)

# Edit model


def entry_edit_post_responce(entry: Entry):
    # obj param help to autofill form from entry by comparing attributes
    form = EntryForm(request.form, obj=entry)
    if form.validate():
        tags = form.save_new_tags()
        for tag in tags:
            db.session.add(tag)
        db.session.commit()

        entry = form.save_entry(entry)
        db.session.add(entry)
        db.session.commit()
        flash(f'Изменения в статье «{entry.title}» сохранены', 'success')
        return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        return render_template('entries/edit.html', entry=entry, form=form)


def entry_edit_get_responce(entry: Entry):
    form = EntryForm(obj=entry)
    return render_template('entries/edit.html', entry=entry, form=form)


@entries.route('/<slug>/edit', methods=['GET', 'POST'])
def edit(slug):
    entry = EntryService.get_entry_or_404(slug)
    if request.method == 'POST':
        return entry_edit_post_responce(entry)
    elif request.method == 'GET':
        return entry_edit_get_responce(entry)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"


def entry_delete_post_responce(entry: Entry):
    entry.status = Entry.STATUS_DELETED
    db.session.add(entry)
    db.session.commit()
    flash(f'Статье «{entry.title}» присвоен статус удаленные', 'success')
    return redirect(url_for('entries.index'))


def entry_delete_get_responce(entry: Entry):
    return render_template('entries/delete.html', entry=entry)


@entries.route('/<slug>/delete', methods=['GET', 'POST'])
def delete(slug):
    entry = EntryService.get_entry_or_404(slug)
    if request.method == 'POST':
        return entry_delete_post_responce(entry)
    elif request.method == 'GET':
        return entry_delete_get_responce(entry)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"
