from .__about__ import (
    __version__,
    __title__,
    __summary__
)
from .mock_op import MockOP

from . import _op
if _op.OP:
    from .response_generator import OPResponseGenerator
else:

    # make pyonepassword dependency a run-time error so it isn't needed if not generating responses
    class OPResponseGenerator:
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("pyonepassword missing, required for OPResponseGenerator")
del _op
