from . import (
    __version__,
    __title__
)
from mock_cli import MockCLIAbout


class MockOPAbout:

    def __str__(self):
        return (
            f"{__title__} version {__version__}\n"
            f"{MockCLIAbout()}"
        )
