import getpass
import os
import sys

from mock_cli import CommandInvocation, ResponseDirectory
parent_path = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
if parent_path not in sys.path:
    sys.path.append(parent_path)

from mock_op import OPResponseGenerator  # noqa: E402


def do_signin():
    # If you've already signed in at least once, you don't need to provide all
    # account details on future sign-ins. Just master password
    my_password = getpass.getpass(prompt="1Password master password:\n")
    # You may optionally provide an account shorthand if you used a custom one during initial sign-in
    # shorthand = "arbitrary_account_shorthand"
    # return OP(account_shorthand=shorthand, password=my_password)
    # Or we'll try to look up account shorthand from your latest sign-in in op's config file
    return OPResponseGenerator(password=my_password)


def do_get_item_1(op: OPResponseGenerator):
    query_name = "get-item-[example-login-1]-[vault-test-data]"
    invocation: CommandInvocation = op.get_item_generate_response(
        "Example Login 1", query_name, vault="Test Data")
    return invocation


def do_get_item_2(op: OPResponseGenerator):
    item_uuid = "nok7367v4vbsfgg2fczwu4ei44"
    query_name = "get-item-by-uuid[example-login-1]"
    invocation: CommandInvocation = op.get_item_generate_response(item_uuid, query_name)
    return invocation


def do_get_item_3(op: OPResponseGenerator):
    item_uuid = "nok7367v4vbsfgg2fczwu4ei44"
    query_name = "get-item-[example-login-2]-[fields-username-password]"
    invocation: CommandInvocation = op.get_item_generate_response(
        item_uuid, query_name, fields="username,password")
    return invocation


def do_get_item_4(op: OPResponseGenerator):
    # 'Example Login' --vault Archive
    query_name = "get-item-[example-login]-[vault-archive]"
    invocation = op.get_item_generate_response("Example Login", query_name, vault="Archive")
    return invocation


def do_get_item_5(op: OPResponseGenerator):
    # 'Example Login' --vault Archive
    item_uuid = "ykhsbhhv2vf6hn2u4qwblfrmg4"
    query_name = "get-item-by-uuid[example-login]-[vault-private]"
    invocation = op.get_item_generate_response(item_uuid, query_name, vault="Private")
    return invocation


def do_get_document(op: OPResponseGenerator):
    document_name = "Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp"
    query_name = "get-document-[spongebob image]"
    invocation: CommandInvocation = op.get_document_generate_response(document_name, query_name)
    return invocation


def do_get_invalid_item(op: OPResponseGenerator):
    item_name = "Invalid Item"
    query_name = "get-item-[invalid-item]"
    invocation: CommandInvocation = op.get_item_generate_response(item_name, query_name)
    return invocation


if __name__ == "__main__":
    try:
        op = do_signin()
    except Exception as e:
        print(str(e))
        exit(1)
    directory_path = "~/.config/mock-op/response-directory.json"
    resopnse_dir = "~/.config/mock-op/responses"
    directory = ResponseDirectory(directory_path, create=True, response_dir=resopnse_dir)

    invocation = do_get_item_1(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_item_2(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_item_3(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_item_4(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_item_5(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_document(op)
    directory.add_command_invocation(invocation, save=True)

    invocation = do_get_invalid_item(op)
    directory.add_command_invocation(invocation, save=True)
