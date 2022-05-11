import sys
from datetime import datetime
from random import choice
from string import ascii_letters, digits


class MockOPSigninResponse:
    TOKEN_LEN = 43
    ERROR_STATUS = 1
    SUCCESS_STATUS = 0
    ERROR_TEMPLATE = "[ERROR] {} Authentication: DB: 401: Unauthorized\n"
    SUCCESS_TEMPLATE = (
        "export OP_SESSION_{}=\"{}\"\n"
        "# This command is meant to be used with your shell's eval function.\n"
        "# Run 'eval $(op signin {})' to sign in to your 1Password account.\n"
        "# Use the --raw flag to only output the session token.\n"
    )

    def __init__(self, shorthand, signin_success=True, raw=True):
        if signin_success:
            token = self._generate_token()
            if raw:
                self._output = token
            else:
                self._output = self.SUCCESS_TEMPLATE.format(
                    shorthand, token, shorthand)
            self._error_output = None
            self.exit_status = self.SUCCESS_STATUS
        else:
            _timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            self._output = None
            self._error_output = self.ERROR_TEMPLATE.format(_timestamp)
            self.exit_status = self.ERROR_STATUS

    def _generate_token(self):
        string_format = ascii_letters + digits
        _token = "".join(choice(string_format)
                         for x in range(0, self.TOKEN_LEN))
        return _token

    def respond(self, *args):
        if self._output is not None:
            sys.stdout.write(self._output)
        if self._error_output is not None:
            sys.stderr.write(self._error_output)

        return self.exit_status
