#!/usr/bin/env python3
import argparse
import os
from argparse import SUPPRESS as ARGPARSE_SUPRESS
from argparse import ArgumentParser
from pathlib import Path

from mock_cli import MockCommand

from .signin_responses import MockOPSigninResponse

RESPONSE_DIRECTORY_PATH = Path(
    Path.home(), ".config", "mock-op", "response-directory.json")

RESP_DIR_ENV_NAME = "MOCK_OP_RESPONSE_DIRECTORY"
SIGNIN_SUCCESS_ENV_NAME = "MOCK_OP_SIGNIN_SUCCEED"
SIGNIN_SHORTHAND_ENV_NAME = "MOCK_OP_SIGNIN_SHORTHAND"
USES_BIO_ENV_NAME = "MOCK_OP_SIGNIN_USES_BIO"
STATE_DIR_ENV_NAME = "MOCK_OP_STATE_DIR"


class MockOPSigninException(Exception):
    pass


class MockOP:
    SIGNIN_CMD = "signin"

    def __init__(self, arg_parser=None, response_directory=None):
        if arg_parser is None:
            arg_parser = self._mock_op_arg_parser()
        self._arg_parser = arg_parser
        self._state_dir = os.environ.get(STATE_DIR_ENV_NAME)

        if response_directory is None:
            response_directory = os.environ.get(RESP_DIR_ENV_NAME)
        self._response_directory = response_directory

    @property
    def response_directory_path(self):
        return self._response_directory

    def _mock_op_arg_parser(self) -> ArgumentParser:
        parser = ArgumentParser()
        parser.add_argument("--account", metavar="account",
                            help="use the account with this identifier")
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
        # parser_signin.add_argument("sign_in_address", nargs="?", default=None)
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
        parser_item_subcmd.add_argument(
            "--fields", help="Only return data from these fields. Use 'label=' to get the field by name or 'type=' to filter fields by type.", choices=["type=otp"])

        parser_item_subcmd = parser_item_subparsers.add_parser(
            "list", description="List items.", help="List items")
        parser_item_subcmd.add_argument(
            "--vault", help="Look for the item in this vault.")
        parser_item_subcmd.add_argument(
            "--include-archive", help="Include items in the Archive.", action='store_true'
        )
        parser_item_subcmd.add_argument(
            "--categories", help="Only list items in these categories (comma-separated).")

        # -- op item template --
        parser_item_subcmd = parser_item_subparsers.add_parser(
            "template", description="Manage templates.", help="Get a list of templates")

        parser_item_template_subparsers = parser_item_subcmd.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)

        # -- op item template list --
        parser_template_subcmd = parser_item_template_subparsers.add_parser(
            "list", description="Lists available item type templates.", help="Get a list of templates")
        parser_template_subcmd.add_argument(
            "list", action="store_true", help=argparse.SUPPRESS)

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

        # group get
        parser_group_subcmd = parser_group_subparsers.add_parser(
            "get", description="Get details about a group", help="Get details about a group")
        parser_group_subcmd.add_argument(
            "group", metavar="{ <groupName> | <groupID> }", help="The group name or ID")

        # group list
        parser_group_subcmd = parser_group_subparsers.add_parser(
            "list", description="List groups.", help="List groups")
        parser_group_subcmd.add_argument(
            "list", help="List groups", action='store_true')
        parser_group_subcmd.add_argument(
            "--user", help=" List groups that a user belongs to.")
        parser_group_subcmd.add_argument(
            "--vault", help="List groups who have direct access to vault.")
        # -- user --
        parser_user = subparsers.add_parser(
            "user", help="Perform CRUD operations on the groups of users in your 1Password account")
        parser_user_subparsers = parser_user.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)

        # user get
        parser_user_subcmd = parser_user_subparsers.add_parser(
            "get", description="Get details about a user", help="Get details about a user")
        parser_user_subcmd.add_argument(
            "user", metavar="{ <email> | <name> | <userID> }", help="The user email address, name, or ID")

        # user list
        parser_user_subcmd = parser_user_subparsers.add_parser(
            "list", description="List users.", help="List users")
        parser_user_subcmd.add_argument(
            "list", help="List users", action='store_true')
        parser_user_subcmd.add_argument(
            "--group", help=" List users who belong to a group.")
        parser_user_subcmd.add_argument(
            "--vault", help="List users who have direct access to vault."
        )

        # -- vault --
        parser_vault = subparsers.add_parser(
            "vault", help="Manage permissions and perform CRUD operations on your 1Password vaults")
        parser_vault_subparsers = parser_vault.add_subparsers(
            title="Available Commands", metavar="[command]", dest="subcommand", required=True)

        # vault get
        parser_vault_subcmd = parser_vault_subparsers.add_parser(
            "get", description="Get details about a vault", help="Get details about a vault")
        parser_vault_subcmd.add_argument(
            "vault", metavar="{ <vaultName> | <vaultID> }", help="The user email address, name, or ID")

        # vault list
        parser_vault_subcmd = parser_vault_subparsers.add_parser(
            "list", description="List vaults.", help="List all vaults in the account")
        parser_vault_subcmd.add_argument(
            "list", help=ARGPARSE_SUPRESS, action='store_true')
        parser_vault_subcmd.add_argument(
            "--group", metavar="string", help="List vaults a group has access to.")
        parser_vault_subcmd.add_argument(
            "--user", metavar="string", help="List vaults that a given user has access to.")

        # -- whoami --
        _ = subparsers.add_parser(
            "whoami", help="Get information about a signed-in account")

        return parser

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
        if parsed.account:
            account = parsed.account
        else:
            account = os.environ.get(SIGNIN_SHORTHAND_ENV_NAME)

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

        if account is None and not self._uses_bio():
            raise MockOPSigninException("No account identifier provided")

        response = MockOPSigninResponse(
            account, signin_success=signin_success, raw=raw)
        exit_status = response.respond([])
        return exit_status

    def respond(self, args):
        if self.SIGNIN_CMD in args:
            exit_status = self._handle_signin(args)
        else:
            cmd = MockCommand(
                response_directory=self._response_directory, state_dir=self._state_dir)
            exit_status = cmd.respond(args)

        return exit_status
