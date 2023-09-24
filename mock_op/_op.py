import logging

try:
    from pyonepassword import OP
    from pyonepassword import logging as op_logging
    from pyonepassword._field_assignment import OPFieldTypeEnum
    from pyonepassword._op_cli_argv import _OPArgv
    from pyonepassword.api.authentication import (
        EXISTING_AUTH_AVAIL,
        EXISTING_AUTH_IGNORE,
        EXISTING_AUTH_REQD
    )
    from pyonepassword.api.exceptions import (
        OPAuthenticationException,
        OPCLIPanicException,
        OPSigninException
    )
    from pyonepassword.api.object_types import OPItemList, OPPasswordRecipe
    # ugh need to add this to API
    from pyonepassword.op_items.password_recipe import (
        OPInvalidPasswordRecipeException
    )
    from pyonepassword.py_op_exceptions import OPWhoAmiException
except ImportError as e:
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    logger = logging.getLogger()
    logger.error(f"Unable to import from pyonepassword: {e}")
    OP = None
    op_logging = None
    OPFieldTypeEnum = None
    _OPArgv = None
    EXISTING_AUTH_AVAIL = None
    EXISTING_AUTH_IGNORE = None
    EXISTING_AUTH_REQD = None
    OPAuthenticationException = None
    OPCLIPanicException = None
    OPSigninException = None
    OPItemList = None
    OPPasswordRecipe = None
    OPInvalidPasswordRecipeException = None
    OPWhoAmiException = None
