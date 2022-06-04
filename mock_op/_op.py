try:
    from pyonepassword import OP, OPNotSignedInException
    from pyonepassword._op_cli_argv import _OPArgv
except ImportError:
    _OPArgv = None
    OP = None
    OPNotSignedInException = None
