from .app import app, db  # import our Flask app
from .models import Tag, Entry

from .controllers import origin
from .controllers.entries import entries

app.register_blueprint(entries, url_prefix='/entries')

if __name__ == '__main__':
    app.run()
