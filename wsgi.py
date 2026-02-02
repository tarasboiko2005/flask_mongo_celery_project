from flask_migrate import Migrate

from app.extensions import db
from app.factory import create_app

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run()
