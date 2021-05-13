from typing import List, Union

from sqlalchemy.orm.query import Query
from collections import namedtuple
from ...models import Entry, Tag
from ...app import db
from ...utils import slugify

DummyTag = namedtuple("DummyTag", ['name', 'slug'])
CreatedTags = namedtuple("CreatedTags", ['new_tags', 'existed_tags'])


class TagService:

    @classmethod
    def get_tag_by_slug(cls, slug: str) -> Tag:
        tag = Tag.query.filter(Tag.slug == slug).first_or_404()
        return tag

    @classmethod
    def get_tag_list_ordered_by_name(cls) -> Query:
        tags = Tag.query.order_by(Tag.name)
        return tags

    @classmethod
    def get_tags_by_slug_multiple(cls, slug_list: List[str]) -> Union[None, Query]:
        query_filter = Tag.slug == ""
        f_empty = False

        for slug in slug_list:
            query_filter |= Tag.slug == slug
            if Tag.query.filter(Tag.slug == slug).count() == 0:
                f_empty = True
                break

        if f_empty:
            return None

        tags = Tag.query.filter(query_filter).all()
        return tags

    @classmethod
    def create_tags_from_name_list(csl, name_list):
        tag_slugs = [slugify(name) for name in name_list]

        slug_names = [DummyTag(*elem)
                      for elem in zip(name_list, tag_slugs)]

        existing_tags = Tag.query.filter(
            Tag.slug.in_(tag_slugs)).all()
        existing_slugs = [tag.slug for tag in existing_tags]

        new_tags = filter(
            lambda x: x.slug not in existing_slugs, slug_names)

        new_tags = [Tag(name=dummy_tag.name)
                    for dummy_tag in new_tags]

        return CreatedTags(new_tags, list(existing_tags))

    @classmethod
    def save(cls, tag: Tag):
        db.session.add(tag)
        db.session.commit()

    @classmethod
    def save_tag_list(cls, tag_list: List[Tag]):
        for tag in tag_list:
            db.session.add(tag)
        db.session.commit()
