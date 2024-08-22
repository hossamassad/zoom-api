import logging
from flask import Flask
from flask_appbuilder import AppBuilder, SQLA
from flask_migrate import Migrate
from flask_cors import CORS
from db_service.app.config import ACCEPTED_ORIGINS

"""
 Logging configuration
"""

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
cors = CORS(app, origins=ACCEPTED_ORIGINS)
app.config.from_pyfile("config.py")
db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

migrate = Migrate(app, db)

from db_service.app.apis.model_apis import *

from db_service.app.apis.core_entities_apis.users_api import CustomSecurityApi
from db_service.app.apis.model_apis.zoom_api import ZoomApi
from db_service.app.models import *





appbuilder.add_api(CustomSecurityApi)
appbuilder.add_api(ZoomApi)



db.create_all()
