from typing import List, Union
from sqlalchemy.orm.query import Query
from ...models import Entry, Tag
from wtforms import Form
from ...app import db
# from dataclasses import dataclass


# @dataclass
# class EntryData:
#     title : str
#     slug : str
#     body : str
#     status = int
#     type = int


class EntryService:
    VALID_STATUSES = (Entry.STATUS_DRAFT, Entry.STATUS_PUBLIC)
    VALID_TYPES = (Entry.TYPE_MICRO, Entry.TYPE_MAJOR)

    @classmethod
    def get_entry_by_slug(cls, slug: str) -> Entry:
        ''' Get entry from entries list by entry's slug
        '''
        return Entry.query.filter(
            (Entry.slug == slug) & (Entry.status.in_(cls.VALID_STATUSES))
        ).first_or_404()

    @classmethod
    def get_entries_ordered_by_date(cls) -> Query:
        ''' Get entries list
        '''
        return Entry.query.order_by(Entry.created_timestamp.desc())

    @classmethod
    def get_entries_by_tag(cls, tag: Tag) -> Query:
        ''' Get entries by tag
        '''
        entries = tag.entries.order_by(Entry.created_timestamp.desc())
        return entries

    @classmethod
    def get_entries_by_tags(cls, tags: List[Tag]) -> Query:
        q_entries = [tag.entries for tag in tags]
        entries = q_entries[0].intersect(
            *q_entries[1:]).order_by(Entry.created_timestamp.desc())

        return entries

    @classmethod
    def filter_entries_by_validity(cls, query_entries: Query) -> Query:
        ''' Filtering entries by valid statuses
        '''
        return query_entries.filter(Entry.status.in_(cls.VALID_STATUSES))

    @classmethod
    def entry_list_search(cls, query_entries: Query, search: str) -> Query:
        ''' Filtering entries by containing search string within body or title 
        '''
        query_entries_validated = cls.filter_entries_by_validity(query_entries)
        if search:
            search_result = query_entries_validated.filter(
                (Entry.body.contains(search)) | (Entry.title.contains(search)))
            return search_result
        else:
            return query_entries_validated

    @classmethod
    def delete_entry(cls, entry):
        entry.status = Entry.STATUS_DELETED
        db.session.add(entry)
        db.session.commit()
        return entry

    @classmethod
    def get_new_entry(cls):
        return Entry()

    @classmethod
    def save_entry(entry: Entry):
        entry.generate_slug()
        db.session.add(entry)
        db.session.commit()
        return entry
