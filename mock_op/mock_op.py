#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from mock_cli import MockCommand

from .mock_op_argument_parser import mock_op_arg_parser
from .signin_responses import MockOPSigninResponse

RESPONSE_DIRECTORY_PATH = Path(
    Path.home(), ".config", "mock-op", "response-directory.json")

RESP_DIR_ENV_NAME = "MOCK_OP_RESPONSE_DIRECTORY"
SIGNIN_SUCCESS_ENV_NAME = "MOCK_OP_SIGNIN_SUCCEED"
SIGNIN_ACCOUNT_ENV_NAME = "MOCK_OP_SIGNIN_ACCOUNT"
USES_BIO_ENV_NAME = "MOCK_OP_SIGNIN_USES_BIO"
STATE_DIR_ENV_NAME = "MOCK_OP_STATE_DIR"
CLI_VER_ENV_NAME = "MOCK_OP_CLI_VER"


class MockOPSigninException(Exception):
    pass


class MockOP:
    SIGNIN_CMD = "signin"
    VERSION_OPTIONS = ["--version", "-v"]

    def __init__(self, arg_parser=None, response_directory=None):
        if arg_parser is None:
            arg_parser = mock_op_arg_parser()
        self._arg_parser = arg_parser
        self._state_dir = os.environ.get(STATE_DIR_ENV_NAME)

        if response_directory is None:
            response_directory = os.environ.get(RESP_DIR_ENV_NAME)
        if self._state_dir and response_directory:
            msg = f"State configuration [{self._state_dir}] and response directory [{response_directory}] provided. Only one can be used"
            raise Exception(msg)
        self._response_directory = response_directory

    @property
    def response_directory_path(self):
        return self._response_directory

    def parse_args(self, argv=None):
        if argv is None:
            parsed = self._arg_parser.parse_args()
        else:
            parsed = self._arg_parser.parse_args(argv)
        return parsed

    def _uses_bio(self):
        uses_bio = os.environ.get(USES_BIO_ENV_NAME)
        if uses_bio not in ["0", "1"]:
            raise MockOPSigninException(
                f"{USES_BIO_ENV_NAME} environment variable should be 0 or 1")
        if uses_bio == "0":
            uses_bio = False
        elif uses_bio == "1":
            uses_bio = True
        else:
            raise Exception(f"unknown uses_bio value {uses_bio}")
        return uses_bio

    def _handle_signin(self, args):
        signin_success = False
        signin_success_val: str | None = os.environ.get(
            SIGNIN_SUCCESS_ENV_NAME)
        parser = mock_op_arg_parser()

        # returns a two item tuple containing the populated
        # namespace and the list of remaining argument strings
        parsed = parser.parse_known_args(args)[0]
        raw = parsed.raw
        if parsed.account:
            account = parsed.account
        else:
            account = os.environ.get(SIGNIN_ACCOUNT_ENV_NAME)

        if signin_success_val is None:
            raise MockOPSigninException(
                "{} environment variable not found".format(SIGNIN_SUCCESS_ENV_NAME))
        if signin_success_val not in ["0", "1"]:
            raise MockOPSigninException(
                "{} environment variable should be 0 or 1".format(SIGNIN_SUCCESS_ENV_NAME))
        elif signin_success_val == "0":
            signin_success = False
        elif signin_success_val == "1":
            signin_success = True

        if account is None and not self._uses_bio():
            raise MockOPSigninException("No account identifier provided")

        response = MockOPSigninResponse(
            account, signin_success=signin_success, raw=raw)
        exit_status = response.respond([])
        return exit_status

    def _cli_version_override(self, args):
        cli_ver_output = None
        exit_status = None

        for option in self.VERSION_OPTIONS:
            if option in args:
                version = os.environ.get(CLI_VER_ENV_NAME)
                if version:
                    version = f"{version}\n"
                    cli_ver_output = version.encode("utf-8")
                    exit_status = 0
                    break
        return (cli_ver_output, exit_status)

    def respond(self, args, input):
        if self.SIGNIN_CMD in args:
            exit_status = self._handle_signin(args)
        else:
            version_override, exit_status = self._cli_version_override(args)
            if version_override:
                MockCommand.write_binary_output(sys.stdout, version_override)
            else:
                cmd = MockCommand(
                    response_directory=self._response_directory, state_dir=self._state_dir)
                exit_status = cmd.respond(args, input=input)

        return exit_status
