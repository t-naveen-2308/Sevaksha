from library_app.utils import DecoratedBlueprint
from library_app.utils import handle_exceptions, login_required

librarian = DecoratedBlueprint(
    "librarian",
    __name__,
    decorators=[login_required(role="librarian"), handle_exceptions],
)

from .routes import *
