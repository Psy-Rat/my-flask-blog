import wtforms
from wtforms.validators import DataRequired
from models import Entry


class EntryForm(wtforms.Form):
    title = wtforms.StringField('Название', validators=[DataRequired()])
    body = wtforms.TextAreaField('Контент', validators=[DataRequired()])
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
