from flask import Blueprint
from flask_restful import Api
import log

logging = log.getLogger("api")

api = Blueprint("other_api", __name__, url_prefix="/api")
api_restful = Api(api)

from wallet.app.api.wallet.key import *
