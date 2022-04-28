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
USES_BIO_ENV_NAME = "MOCK_OP_SIGNIN_USES_BIO"


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
        parser.add_argument(
            "--version", help="version for op", action='store_true')

        parser.add_argument(
            "--format", help="Use this output format. Can be 'human-readable' or 'json'.")

        subparsers = parser.add_subparsers(
            description="Available Commands", metavar="[command]", dest="command", required=False)

        # -- account --
        parser_account = subparsers.add_parser(
            "account", help="Manage your locally configured 1Password accounts")
        parser_account_subparsers = parser_account.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)
        parser_acct_subcmd = parser_account_subparsers.add_parser(
            "list", help="List users and accounts set up on this device")
        parser_acct_subcmd.add_argument("list", action="store_true")

        # parser_account.add_argument("sign_in_address", nargs="?", default=None)
        # parser_signin.add_argument(
        #     "-r", "--raw", help="only return the session token", action='store_true')

        # -- signin --
        parser_signin = subparsers.add_parser(
            "signin", help="Sign in to a 1Password account")
        parser_signin.add_argument("sign_in_address", nargs="?", default=None)
        parser_signin.add_argument(
            "-r", "--raw", help="only return the session token", action='store_true')

        # -- item --
        parser_item = subparsers.add_parser(
            "item", help="Perform CRUD operations on the 1Password items in your vaults")

        parser_item_subparsers = parser_item.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)

        parser_item_subcmd = parser_item_subparsers.add_parser(
            "get", description="Return details about an item.", help="Get an item's details")
        parser_item_subcmd.add_argument(
            "item", metavar="<itemName>", help="The item to get")
        parser_item_subcmd.add_argument(
            "--vault", help="Look for the item in this vault.")

        # -- document --
        parser_document = subparsers.add_parser(
            "document", help="Perform CRUD operations on Document items in your vaults")
        parser_document_subparsers = parser_document.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)
        parser_doc_subcmd = parser_document_subparsers.add_parser(
            "get", description="Download a document and print the contents.", help="Download a document")
        parser_doc_subcmd.add_argument(
            "document", metavar="<documentName>", help="The document to download")

        parser_doc_subcmd.add_argument(
            "--vault", help="Look for the document in this vault")

        # -- group --
        parser_group = subparsers.add_parser(
            "group", help="Perform CRUD operations on the groups of users in your 1Password account")
        parser_group_subparsers = parser_group.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)
        parser_group_subcmd = parser_group_subparsers.add_parser(
            "get", description="Get details about a group", help="Get details about a group")
        parser_group_subcmd.add_argument(
            "group", metavar="{ <groupName> | <groupID> }", help="The group name or ID")

        # -- user --
        parser_user = subparsers.add_parser(
            "user", help="Perform CRUD operations on the groups of users in your 1Password account")
        parser_user_subparsers = parser_user.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)
        parser_user_subcmd = parser_user_subparsers.add_parser(
            "get", description="Get details about a user", help="Get details about a user")
        parser_user_subcmd.add_argument(
            "user", metavar="{ <email> | <name> | <userID> }", help="The user email address, name, or ID")

        # -- vault --
        parser_vault = subparsers.add_parser(
            "vault", help="Manage permissions and perform CRUD operations on your 1Password vaults")
        parser_vault_subparsers = parser_vault.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)
        parser_vault_subcmd = parser_vault_subparsers.add_parser(
            "get", description="Get details about a vault", help="Get details about a vault")
        parser_vault_subcmd.add_argument(
            "vault", metavar="{ <vaultName> | <vaultID> }", help="The user email address, name, or ID")

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

        if shorthand is None and not self._uses_bio():
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
