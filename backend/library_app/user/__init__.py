from library_app.utils import DecoratedBlueprint
from library_app.utils import handle_exceptions, login_required

user = DecoratedBlueprint(
    "user", __name__, decorators=[login_required(role="user"), handle_exceptions]
)

from .routes import *
