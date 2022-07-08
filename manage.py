import os
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

import wpath
import log
from models import db
from wallet.app.app import create_app
from models.wallet.key import Key


app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db, directory="migrations-wallet")

manager.add_command("shell", Shell())
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()
