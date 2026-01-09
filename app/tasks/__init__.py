from .image_tasks import register_image_tasks
from .parser_tasks import register_parser_tasks

def register_task(celery):
    """
    Register all Celery tasks (image + parser)
    """
    register_image_tasks(celery)
    register_parser_tasks(celery)