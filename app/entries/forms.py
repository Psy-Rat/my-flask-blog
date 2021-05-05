import wtforms
from models import Entry


class EntryForm(wtforms.Form):
    title = wtforms.StringField('Название')
    body = wtforms.TextAreaField('Контент')
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
