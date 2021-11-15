try:
    from pyonepassword import OP, OPNotSignedInException
except ImportError:
    OP = None
    OPNotSignedInException = None
