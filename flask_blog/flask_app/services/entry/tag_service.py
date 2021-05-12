from typing import List, Union

from sqlalchemy.orm.query import Query
from ...models import Entry, Tag


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
