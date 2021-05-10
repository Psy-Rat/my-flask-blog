from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy


from .config import DebugConfig

############
# App
############
app = Flask(__name__)

app.config.from_object(DebugConfig)  # ToDo
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)
