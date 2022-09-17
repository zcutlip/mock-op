from datetime import datetime
from random import choice
from string import ascii_letters, digits

from mock_cli import MockCommand, CommandResponse


class MockOPSigninResponse(MockCommand):
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
        changes_state = False
        if signin_success:
            changes_state = True
            token = self._generate_token()
            if raw:
                output = token
            else:
                output = self.SUCCESS_TEMPLATE.format(
                    shorthand, token, shorthand)
            error_output = ''
            exit_status = self.SUCCESS_STATUS
        else:
            _timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            output = ''
            error_output = self.ERROR_TEMPLATE.format(_timestamp)
            exit_status = self.ERROR_STATUS

        output = output.encode("utf-8")
        error_output = error_output.encode("utf-8")

        resp_dict = {
            "stdout": None,
            "stderr": None,
            "changes_state": changes_state,
            "exit_status": exit_status,
            "name": "op sign-in response"
        }
        super().__init__()
        response = CommandResponse(
            resp_dict, None, output=output, error_output=error_output)
        self._response = response

    def _get_response_directory(self, *args):
        return None

    def get_response(self, *args) -> CommandResponse:
        return self._response

    def _generate_token(self):
        string_format = ascii_letters + digits
        _token = "".join(choice(string_format)
                         for x in range(0, self.TOKEN_LEN))
        return _token
