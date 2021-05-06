import datetime
import re
from transliterate import translit

from app import db


############
# Models
############
def slugify(s):
    s = s.replace('-', '*')
    trans_s = translit(s, reversed=True)
    trans_s = trans_s.replace('-', '')
    trans_s = trans_s.replace('*', '-')

    return re.sub('[^\w]+', '-', trans_s).lower()


entry_tags = db.Table('entry_tags',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                      db.Column('entry_id', db.Integer,
                                db.ForeignKey('entry.id'))
                      )


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


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), nullable=False, unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return f'<Tag {self.name}>'
