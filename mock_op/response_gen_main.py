import getpass

from argparse import ArgumentParser
from pathlib import Path

from mock_cli import CommandInvocation, ResponseDirectory

from ._op import OPNotSignedInException
from .response_generator import OPResponseGenerator
from .response_generator_config import OPResponseGenConfig


def resp_gen_parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "config", help="Config file describing 'op' responses to generate")

    parsed = parser.parse_args()
    return parsed


def do_signin():
    # If you've already signed in at least once, you don't need to provide all
    # account details on future sign-ins. Just master password
    try:
        op = OPResponseGenerator(
            use_existing_session=True, password_prompt=False)
    except OPNotSignedInException:
        my_password = getpass.getpass(prompt="1Password master password:\n")
        op = OPResponseGenerator(password=my_password)
    return op


def do_get_item(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    item_id = query_definition["item_identifier"]
    vault = query_definition.get("vault")
    invocation = op.get_item_generate_response(
        item_id, query_name, vault=vault)
    return invocation


def do_get_document(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    # Getting a document is a two-step process
    # first:
    #   op get item <document identifier"
    # to get JSON details describing the document, including it's original filename
    # second:
    #   op get document <document identifier>
    # to get the actual data representing the document

    # query 1: get the document filename
    query_name_filename = f"{query_name}-filename"
    item_filename_invocation = do_get_item(
        op, query_name_filename, query_definition)

    # query 2: get the document bytes
    vault = query_definition.get("vault")

    # if we want to simulate document bytes being missing
    # even though the "document item" is present, specify
    # an alternate document identifier for step 2, that is known to fail
    alt_item_id = query_definition.get("item_identifier_alternate")
    item_id = query_definition["item_identifier"]
    document_invocation = op.get_document_generate_response(
        item_id, query_name, vault=vault, alternate_name=alt_item_id)

    # return both invocations
    return document_invocation, item_filename_invocation


def do_get_vault(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    vault_id = query_definition["vault_identifier"]
    invocation = op.get_vault_generate_response(vault_id, query_name)
    return invocation


def do_get_user(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    user_id = query_definition["user_identifier"]
    invocation = op.get_user_generate_response(user_id, query_name)
    return invocation


def do_get_group(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    group_id = query_definition["group_identifier"]
    invocation = op.get_group_generate_response(group_id, query_name)
    return invocation


def do_cli_version(op: OPResponseGenerator, query_name, _unused_query_definition) -> CommandInvocation:
    invocation = op.cli_version(query_name)
    return invocation


def do_list_items(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    categories = query_definition.get("categories", [])
    include_archive = query_definition.get("include_archive", False)
    tags = query_definition.get("tags", [])
    vault = query_definition.get("vault", None)

    invocation = op.list_items_generate_response(
        query_name, categories=categories, include_archive=include_archive,
        tags=tags, vault=vault)

    return invocation


def main():
    args = resp_gen_parse_args()
    conf_path = args.config
    generator_config = OPResponseGenConfig(conf_path)
    config_dir = Path(generator_config.config_path).expanduser()

    respdir_json_file = Path(
        config_dir, generator_config.respdir_json_file)
    response_path = Path(config_dir, generator_config.response_path)

    try:
        op = do_signin()
    except Exception as e:
        print(str(e))
        exit(1)
    directory = ResponseDirectory(
        respdir_json_file, create=True, response_dir=response_path)

    for query_name, query_definition in generator_config.items():
        if not query_definition.enabled:
            continue

        if query_definition.type == "get-item":
            invocation = do_get_item(op, query_name, query_definition)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        elif query_definition.type == "get-document":
            document_invocation, filename_invocation = do_get_document(
                op, query_name, query_definition)

            directory.add_command_invocation(
                filename_invocation, overwrite=True)

            directory.add_command_invocation(
                document_invocation, overwrite=True, save=True)

        elif query_definition.type == "get-vault":
            invocation = do_get_vault(op, query_name, query_definition)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        elif query_definition.type == "get-user":
            invocation = do_get_user(op, query_name, query_definition)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        elif query_definition.type == "get-group":
            invocation = do_get_group(op, query_name, query_definition)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        elif query_definition.type == "cli-version":
            invocation = do_cli_version(op, query_name)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        elif query_definition.type == "list-items":
            invocation = do_list_items(op, query_name, query_definition)
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)

        else:
            raise Exception(f"Unknown query type: {query_definition['type']}")


if __name__ == "__main__":
    main()
