import peewee
from playhouse.flask_utils import FlaskDB

database = peewee.SqliteDatabase("db.db")
db = FlaskDB(database=database)
