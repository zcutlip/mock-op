import sys
import shlex

from mock_cli import (
    ResponseDirectory,
    ResponseDirectoryException,
    ResponseLookupException
)
from mock_cli.argv_conversion import argv_from_string

from .mock_op import MockOP


def mock_op_main():
    mock_op_cmd = MockOP()
    # We parse args in order to fail on args we don't understand
    # even though we don't actually use them
    mock_op_cmd.parse_args()

    args = sys.argv[1:]
    try:
        exit_status = mock_op_cmd.respond(args)
    except (ResponseDirectoryException, ResponseLookupException) as e:
        print(f"Error looking up response: [{e}]", file=sys.stderr)
        exit_status = -1

    return exit_status


def list_invocations_main():
    mock_op_cmd = MockOP()
    resp_dir_path = mock_op_cmd.response_directory_path
    directory = ResponseDirectory(resp_dir_path)

    commands = directory.commands

    for cmd in commands.keys():
        cmd_args = argv_from_string(cmd)
        arg_string = shlex.join(cmd_args)

        print(f"{arg_string}")


if __name__ == "__main__":
    exit(mock_op_main())
