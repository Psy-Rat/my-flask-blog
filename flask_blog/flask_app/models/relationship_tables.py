from ..app import db

entry_tags = db.Table('entry_tags',
                      db.Column(
                          'tag_id',
                          db.Integer,
                          db.ForeignKey('tag.id')),

                      db.Column(
                          'entry_id',
                          db.Integer,
                          db.ForeignKey('entry.id'))
                      )
