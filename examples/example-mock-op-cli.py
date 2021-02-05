import os
import sys
from mock_cli import (
    ResponseDirectoryException,
    ResponseLookupException
)

parent_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
if parent_path not in sys.path:
    sys.path.append(parent_path)

from mock_op import MockOP  # noqa: E402


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
