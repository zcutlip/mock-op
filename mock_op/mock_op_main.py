import os
import sys

from mock_cli import ResponseDirectoryException, ResponseLookupException
from mock_cli.hashing import digest_input

from .mock_op import MockOP

READ_INPUT_FILE_ENV_NAME = "MOCK_OP_READ_INPUT_FILE"


def optionally_replace_stdin():
    # for debugging purposes in vscode which can't
    # pipe to stdin of the target
    if os.environ.get(READ_INPUT_FILE_ENV_NAME):
        fh = open(os.environ[READ_INPUT_FILE_ENV_NAME], "rb")
        sys.stdin = fh


def main():
    optionally_replace_stdin()
    mock_op_cmd = MockOP()
    # We parse args in order to fail on args we don't understand
    # even though we don't actually use them
    mock_op_cmd.parse_args()
    input = None
    if not sys.stdin.isatty():
        input = sys.stdin.read()

    args = sys.argv[1:]
    try:
        exit_status = mock_op_cmd.respond(args, input)
    except (ResponseDirectoryException, ResponseLookupException) as e:
        input_hash = digest_input(input)
        err_msg = f"Error looking up response: [{e}]"

        if input_hash:
            err_msg += f", with input hash: {input_hash}"

        print(err_msg, file=sys.stderr)
        exit_status = -1

    return exit_status


if __name__ == "__main__":
    main()
