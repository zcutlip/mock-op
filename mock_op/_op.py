import logging

logging.basicConfig(format="%(message)s", level=logging.DEBUG)
logger = logging.getLogger()

try:
    from pyonepassword import OP
    from pyonepassword._op_cli_argv import _OPArgv
    from pyonepassword.api.exceptions import (OPNotSignedInException,
                                              OPSigninException)
    from pyonepassword.api.authentication import EXISTING_AUTH_AVAIL
except ImportError as e:
    logger.error(f"Unable to import from pyonepassword: {e}")
    OP = None
    OPNotSignedInException = None
    OPSigninException = None
    _OPArgv = None
    EXISTING_AUTH_AVAIL = None
