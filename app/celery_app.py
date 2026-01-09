from app import create_app, make_celery

flask_app = create_app()
celery_app = make_celery(flask_app)