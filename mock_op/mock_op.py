#!/usr/bin/env python3
import os
from argparse import ArgumentParser

from mock_cli import MockCommand

RESPONSE_DIRECTORY_PATH = "~/.config/mock-op/response-directory.json"
RESP_DIR_ENV_NAME = "MOCK_OP_RESPONSE_DIRECTORY"


class MockOP:
    def __init__(self, arg_parser=None, response_directory=None):
        if arg_parser is None:
            arg_parser = self._mock_op_arg_parser()
        self._arg_parser = arg_parser
        if response_directory is None:
            response_directory = self._get_response_directory()
        self._response_directory = response_directory

    @property
    def response_directory_path(self):
        return self._response_directory

    def _mock_op_arg_parser(self):
        parser = ArgumentParser()
        parser.add_argument("--global-flag", help="the global flag")
        subparsers = parser.add_subparsers(
            description="Available Commands", metavar="[command]", dest="command", required=True)
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

        return parser

    def _get_response_directory(self):
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

    def respond(self, args):
        cmd = MockCommand(self._response_directory)
        exit_status = cmd.respond(args)
        return exit_status
