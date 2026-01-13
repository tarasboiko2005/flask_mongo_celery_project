from .image_routes import bp as image_bp
from .parser_routes import bp as parse_bp
from .status_routes import bp as status_bp

blueprints = [image_bp, parse_bp, status_bp]