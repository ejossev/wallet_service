import config as config_env
import datetime
import os

from utl.env import Tenv
from config import MYSQL_WALLET_DATABASE, MYSQL_WALLET_PORT, MYSQL_WALLET_ADDRESS, MYSQL_PASSWORD, MYSQL_USER

env = Tenv()
project_folder = os.path.split(os.path.realpath(__file__))[0]


class Config:
    import Crypto.Util.Padding
    WALLET_SECRET_KEY = Crypto.Util.Padding.pad(env.get("WALLET_SECRET_KEY", require=True).encode(), 16)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    REDIS_URL = config_env.REDIS_URL
    PROPAGATE_EXCEPTIONS = True
    BASEDIR = project_folder

    SQLALCHEMY_DATABASE_URI = (
            env.get("DEV_DATABASE_URL")
            or f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_WALLET_ADDRESS}:{MYSQL_WALLET_PORT}/{MYSQL_WALLET_DATABASE}"
    )
    HTTPS_HOST = config_env.WALLET_HTTPS_HOST
    HTTPS_PORT = config_env.WALLET_HTTPS_PORT
    CERT_FILE = config_env.CERT_FILE
    KEY_FILE = config_env.KEY_FILE
    CA_FILE = config_env.CA_FILE
    DEBUG = config_env.FLASK_DEBUG

    @staticmethod
    def init_app(app):
        pass


WALLET_CONFIG = Config