import wtforms
from wtforms.validators import DataRequired
from collections import namedtuple

from ...services import EntryService, TagService


class TagField(wtforms.StringField):
    def _value(self):
        if self.data:
            return '; '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw = tag_string.split(';')
        tag_names = [name.strip() for name in raw if name.strip()]
        tags = TagService.create_tags_from_name_list(tag_names)
        return [*tags]

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
            (EntryService.VALID_STATUSES[0], 'Черновое'),
            (EntryService.VALID_STATUSES[1], 'Обобществлённое')
        ),
        coerce=int)

    type = wtforms.SelectField(
        'Тип',
        choices=(
            (EntryService.VALID_TYPES[0],  'Твит'),
            (EntryService.VALID_TYPES[1],  'Пост')
        ),
        coerce=int)

    def save_entry(self):
        entry = EntryService.get_new_entry()
        entry = self.modify_entry(entry)
        return entry

    def modify_entry(self, entry):
        self.populate_obj(entry)
        entry = EntryService.save_entry(entry)
        return entry

    def save_new_tags(self):
        new_tags = self.tags.get_new_tags()
        TagService.save_tag_list(new_tags)
        return new_tags
