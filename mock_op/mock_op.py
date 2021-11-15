#!/usr/bin/env python3
import os
from pathlib import Path
from argparse import ArgumentParser

from mock_cli import MockCommand

from .signin_responses import MockOPSigninResponse


RESPONSE_DIRECTORY_PATH = Path(
    Path.home(), ".config", "mock-op", "response-directory.json")

RESP_DIR_ENV_NAME = "MOCK_OP_RESPONSE_DIRECTORY"
SIGNIN_SUCCESS_ENV_NAME = "MOCK_OP_SIGNIN_SUCCEED"
SIGNIN_SHORTHAND_ENV_NAME = "MOCK_OP_SIGNIN_SHORTHAND"


class MockOPSigninException(Exception):
    pass


class MockOP:
    SIGNIN_CMD = "signin"

    def __init__(self, arg_parser=None, response_directory=None):
        if arg_parser is None:
            arg_parser = self._mock_op_arg_parser()
        self._arg_parser = arg_parser
        if response_directory is None:
            response_directory = self.get_response_directory()
        self._response_directory = response_directory

    @property
    def response_directory_path(self):
        return self._response_directory

    def _mock_op_arg_parser(self) -> ArgumentParser:
        parser = ArgumentParser()
        parser.add_argument("--account", metavar="shorthand",
                            help="use the account with this shorthand")
        subparsers = parser.add_subparsers(
            description="Available Commands", metavar="[command]", dest="command", required=True)

        parser_signin = subparsers.add_parser(
            "signin", help="Signs in to a 1Password account and returns a session token.")
        parser_signin.add_argument("sign_in_address", nargs="?", default=None)
        parser_signin.add_argument(
            "-r", "--raw", help="only return the session token", action='store_true')

        parser_get = subparsers.add_parser("get", help="the get command")

        parser_get_subparsers = parser_get.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)

        parser_get_subcmd = parser_get_subparsers.add_parser(
            "document", description="Download & print a document to standard output", help="Download a document")
        parser_get_subcmd.add_argument(
            "document", metavar="<document>", help="The document to get")
        parser_get_subcmd.add_argument(
            "--vault", help="The vault to look up and item from")

        parser_get_subcmd = parser_get_subparsers.add_parser(
            "item", description="Returns details about an item.", help="Get item details")
        parser_get_subcmd.add_argument(
            "item", metavar="<item>", help="The item to get")
        parser_get_subcmd.add_argument(
            "--fields", help="comma-separated list of fields to get about the item")
        parser_get_subcmd.add_argument(
            "--vault", help="The vault to look up and item from")

        parser_get_subcmd = parser_get_subparsers.add_parser(
            "vault", description="Get details about a vault.", help="Get details about a vault")
        parser_get_subcmd.add_argument(
            "vault", metavar="<vault>", help="The vault to get")

        return parser

    @classmethod
    def get_response_directory(cls):
        rdpath = os.environ.get(RESP_DIR_ENV_NAME)
        if not rdpath:
            rdpath = RESPONSE_DIRECTORY_PATH
        return rdpath

    def parse_args(self, argv=None):
        if argv is None:
            parsed = self._arg_parser.parse_args()
        else:
            parsed = self._arg_parser.parse_args(argv)

        return parsed

    def _handle_signin(self, args):
        signin_success = os.environ.get(SIGNIN_SUCCESS_ENV_NAME)
        parser = self._mock_op_arg_parser()

        # returns a two item tuple containing the populated
        # namespace and the list of remaining argument strings
        parsed = parser.parse_known_args(args)[0]
        raw = parsed.raw
        if parsed.sign_in_address:
            shorthand = parsed.sign_in_address
        else:
            shorthand = os.environ.get(SIGNIN_SHORTHAND_ENV_NAME)

        if signin_success is None:
            raise MockOPSigninException(
                "{} environment variable not found".format(SIGNIN_SUCCESS_ENV_NAME))
        if signin_success not in ["0", "1"]:
            raise MockOPSigninException(
                "{} environment variable should be 0 or 1".format(SIGNIN_SUCCESS_ENV_NAME))
        elif signin_success == "0":
            signin_success = False
        elif signin_success == "1":
            signin_success = True

        if shorthand is None:
            raise MockOPSigninException("No account shorthand provided")

        response = MockOPSigninResponse(
            shorthand, signin_success=signin_success, raw=raw)
        exit_status = response.respond()
        return exit_status

    def respond(self, args):
        if self.SIGNIN_CMD in args:
            exit_status = self._handle_signin(args)
        else:
            cmd = MockCommand(self._response_directory)
            exit_status = cmd.respond(args)
        return exit_status
