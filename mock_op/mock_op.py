#!/usr/bin/env python3
import sys
from argparse import ArgumentParser
from mock_cli.mock_cmd import MockCommand


def mock_op_arg_parser():
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


def main():
    # We parse args in order to fail on args we don't understand
    # even though we don't actually use them
    parser = mock_op_arg_parser()
    parser.parse_args()
    response_directory_path = "./response-directory.json"
    cmd = MockCommand(response_directory_path)
    args = sys.argv[1:]
    exit_status = cmd.respond(args)
    return exit_status


if __name__ == "__main__":
    exit(main())
