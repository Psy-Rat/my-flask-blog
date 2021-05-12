from flask import Blueprint, flash, render_template, redirect, url_for, request
from collections import namedtuple

from .forms import EntryForm
from ...helpers import markdown, get_anchors, parse_anchors_as_bootstrap
from ...helpers import render_paginated

from ...services.entry import EntryService, TagService

from ...app import db

DummyTag = namedtuple("DummyTag", ["name"])


entries = Blueprint(
    'entries',
    __name__,
    template_folder='templates')


@entries.route('/')
def index():
    entries = EntryService.get_entries_ordered_by_date()
    return render_paginated('entries/index.html', entries)


@entries.route('/tags/')
def tag_index():
    tags = TagService.get_tag_list_ordered_by_name()
    return render_paginated('entries/index_tag.html', tags)


def single_tag_search(slug):
    tag = TagService.get_tag_by_slug(slug)
    entries = EntryService.get_entries_by_tag(tag)
    return render_paginated('entries/detail_tag.html', entries, tag=tag)


def multiple_tag_search(slug_list):
    ''' 
    '''
    tags = TagService.get_tags_by_slug_multiple(slug_list)
    if tags is None:
        entries = None
        tags = [DummyTag(name=slug) for slug in slug_list]
    else:
        entries = EntryService.get_entries_by_tags(tags)

    return render_paginated('entries/detail_tag.html',
                            entries,
                            tag=tags)


@entries.route('/tags/<slug>/')
def tag_detail(slug):
    if '+' in slug:
        slug_list = slug.split('+')
    else:
        slug_list = [slug]
    # if len(slug_list) == 1:
        # return multiple_tag_search(slug)
    # else:
    return multiple_tag_search(slug_list)


# Creation model
def create_entry_post():
    form = EntryForm(request.form)
    if form.validate():
        result = form.save_entry()
        flash(f'Статья «{result.title}» создана', 'success')
        return redirect(url_for('entries.detail', slug=result.slug))
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
    entry = EntryService.get_entry_by_slug(slug)
    anchors = get_anchors(entry.body)
    main_data = markdown(
        entry.body, anchors, math=True, fenced_code=True)
    anch = parse_anchors_as_bootstrap(
        anchors)
    return render_template('entries/detail.html', entry=entry, rendered_data=main_data, scrollspy=anch)

# Edit model


def entry_edit_post_responce(slug: str):
    # obj param help to autofill form from entry by comparing attributes
    entry = EntryService.get_entry_by_slug(slug)
    form = EntryForm(request.form, obj=entry)
    if form.validate():
        tags = form.save_new_tags()
        entry = form.modify_entry(entry)
        flash(f'Изменения в статье «{entry.title}» сохранены', 'success')
        return redirect(url_for('entries.detail', slug=entry.slug))
    else:
        return render_template('entries/edit.html', entry=entry, form=form)


def entry_edit_get_responce(slug: str):
    entry = EntryService.get_entry_by_slug(slug)
    form = EntryForm(obj=entry)
    return render_template('entries/edit.html', entry=entry, form=form)


@entries.route('/<slug>/edit', methods=['GET', 'POST'])
def edit(slug):
    if request.method == 'POST':
        return entry_edit_post_responce(slug)
    elif request.method == 'GET':
        return entry_edit_get_responce(slug)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"


def entry_delete_post_responce(slug: str):
    entry = EntryService.get_entry_by_slug(slug)
    entry = EntryService.delete_entry(entry)
    flash(f'Статье «{entry.title}» присвоен статус удаленные', 'success')
    return redirect(url_for('entries.index'))


def entry_delete_get_responce(slug: str):
    entry = EntryService.get_entry_by_slug(slug)
    return render_template('entries/delete.html', entry=entry)


@entries.route('/<slug>/delete', methods=['GET', 'POST'])
def delete(slug):
    if request.method == 'POST':
        return entry_delete_post_responce(slug)
    elif request.method == 'GET':
        return entry_delete_get_responce(slug)
    else:
        assert request.method in [
            'GET', 'POST'], "Unexpected behaviour: only get and post requests assumed"
