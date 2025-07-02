from .flask_server import FlaskServer
from .pill_dispenser_dashboard import register_with_app as register_pill_dispenser

__all__ = ["FlaskServer", "register_pill_dispenser"]
