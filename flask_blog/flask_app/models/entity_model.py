import datetime
from ..app import db
from ..utils import slugify

from .relationship_tables import entry_tags


class Entry(db.Model):
    __tablename__ = 'entry'

    STATUS_PUBLIC = 0
    STATUS_DRAFT = 1
    STATUS_DELETED = 2

    TYPE_MICRO = 0
    TYPE_MAJOR = 1

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    body = db.Column(db.Text)
    status = db.Column(db.SmallInteger, default=STATUS_DRAFT)
    type = db.Column(db.SmallInteger, default=TYPE_MICRO)

    created_timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.now)  # , index=True)

    modified_timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now)

    # querying 'TAG'
    # via entry_tags
    # allowing to go from TAG to associated entries
    # instead of it loading all the associated entries, we want a Query object
    tags = db.relationship(
        'Tag',
        secondary=entry_tags,
        backref=db.backref('entries', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Entry, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        self.slug = ''
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f'<Entry: {self.title}>'
