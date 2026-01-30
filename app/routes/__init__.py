from app.routes.image_routes import bp as image_bp
from app.routes.parser_routes import bp as parse_bp
from app.routes.status_routes import bp as status_bp
from app.routes.mcp_routes import mcp_bp
from app.routes.rag_routes import rag_bp
from app.routes.security import security_bp

blueprints = [image_bp, parse_bp, status_bp, mcp_bp, rag_bp, security_bp]