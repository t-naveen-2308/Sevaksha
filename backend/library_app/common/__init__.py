from library_app.utils import DecoratedBlueprint
from library_app.utils import handle_exceptions, login_required

common = DecoratedBlueprint(
    "common",
    __name__,
    decorators=[login_required(role="user or librarian"), handle_exceptions],
)

from .routes import *
