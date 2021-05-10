import wtforms
from wtforms.validators import DataRequired
from collections import namedtuple

from ...models import Entry, Tag, slugify


DummyTag = namedtuple("DummyTag", ['name', 'slug'])


class TagField(wtforms.StringField):
    def _value(self):
        if self.data:
            return '; '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw = tag_string.split(';')
        tag_names = [name.strip() for name in raw if name.strip()]
        tag_slugs = [slugify(name) for name in tag_names]

        slug_names = [DummyTag(*elem)
                      for elem in zip(tag_names, tag_slugs)]

        existing_tags = Tag.query.filter(
            Tag.slug.in_(tag_slugs)).all()
        existing_slugs = [tag.slug for tag in existing_tags]

        new_tags = filter(
            lambda x: x.slug not in existing_slugs, slug_names)

        new_tags = [Tag(name=dummy_tag.name)
                    for dummy_tag in new_tags]
        return list(existing_tags), new_tags

    def process_formdata(self, valuelist):
        if valuelist:

            self.old_tags, self.new_tags = self.get_tags_from_string(
                valuelist[0])
            self.data = self.old_tags + self.new_tags
        else:
            self.old_tags, self.new_tags = []
            self.data = []

    def get_new_tags(self):
        return self.new_tags


class EntryForm(wtforms.Form):
    title = wtforms.StringField('Название', validators=[DataRequired()])
    body = wtforms.TextAreaField('Контент', validators=[DataRequired()])
    tags = TagField('Тэги', description="Теги разделяются точкой с запятой")
    status = wtforms.SelectField(
        'Статус',
        choices=(
            (Entry.STATUS_DRAFT,  'Черновое'),
            (Entry.STATUS_PUBLIC, 'Обобществлённое')
        ),
        coerce=int)

    type = wtforms.SelectField(
        'Тип',
        choices=(
            (Entry.TYPE_MICRO,  'Твит'),
            (Entry.TYPE_MAJOR,  'Пост')
        ),
        coerce=int)

    def save_entry(self, entry):
        self.populate_obj(entry)
        entry.generate_slug()
        return entry

    def save_new_tags(self):
        new_tags = self.tags.get_new_tags()
        return new_tags
