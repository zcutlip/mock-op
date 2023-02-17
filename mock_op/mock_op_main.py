import sys

from mock_cli import ResponseDirectoryException, ResponseLookupException
from mock_cli.hashing import digest_input

from .mock_op import MockOP


def main():
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
