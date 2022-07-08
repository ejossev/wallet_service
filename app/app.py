from flask import Flask, request, render_template, make_response

from server.app.db import init_db, init_redis
from utl.api import rsp_err
from models import db

from wallet.wallet_config import WALLET_CONFIG
import log

logging = log.getLogger("api")


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(WALLET_CONFIG)

    init_db(app)
    init_redis(app)

    @app.errorhandler(404)
    def erro_404(e):
        logging.info(f"404 error:user request unexist url:{request.url}")
        return rsp_err("page not found", status=404)

    @app.errorhandler(500)
    def erro_500(e):
        return rsp_err("server internal error", status=500)

    from .api import api
    app.register_blueprint(api)

    @app.teardown_request
    def teardown_request(exception):
        if exception:
            db.session.rollback()
        db.scope_session.remove()

    return app
