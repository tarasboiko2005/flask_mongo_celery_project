from app.factory import create_app
from app.extensions import make_celery

flask_app = create_app()
celery_app = make_celery(flask_app)