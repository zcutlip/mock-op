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


def item_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    item_id = query_definition["item_identifier"]
    vault = query_definition.get("vault")
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.item_get_generate_response(
        item_id, query_name, vault=vault, expected_ret=expected_return)
    return invocation


def document_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    # Getting a document is a two-step process
    # first:
    #   op get item <document identifier"
    # to get JSON details describing the document, including it's original filename
    # second:
    #   op get document <document identifier>
    # to get the actual data representing the document

    # query 1: get the document filename
    query_name_filename = f"{query_name}-filename"
    item_filename_invocation = item_get(
        op, query_name_filename, query_definition)

    # query 2: get the document bytes
    vault = query_definition.get("vault")
    expected_return = query_definition.get("expected-return", 0)
    expected_return_2 = query_definition.get(
        "expected-return-2", expected_return)

    # if we want to simulate document bytes being missing
    # even though the "document item" is present, specify
    # an alternate document identifier for step 2, that is known to fail
    alt_item_id = query_definition.get("item_identifier_alternate")
    item_id = query_definition["item_identifier"]
    document_invocation = op.document_get_generate_response(
        item_id, query_name, vault=vault, alternate_name=alt_item_id, expected_ret=expected_return_2)

    # return both invocations
    return document_invocation, item_filename_invocation


def vault_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    vault_id = query_definition["vault_identifier"]
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.vault_get_generate_response(
        vault_id, query_name, expected_ret=expected_return)
    return invocation


def user_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    user_id = query_definition["user_identifier"]
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.user_get_generate_response(
        user_id, query_name, expected_ret=expected_return)
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


def account_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.account_list_generate_response(
        query_name, expected_ret=expected_return)
    return invocation


query_type_map = {
    "item-get": item_get,
    "document-get": document_get,
    "vault-get": vault_get,
    "user-get": user_get,
    "get-group": do_get_group,
    "cli-version": do_cli_version,
    "list-items": do_list_items,
    "account-list": account_list
}


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
        try:
            query_func = query_type_map[query_definition['type']]
        except KeyError:
            raise Exception(f"Unknown query type: {query_definition['type']}")

        invocation = query_func(op, query_name, query_definition)
        if isinstance(invocation, tuple):
            document_invocation, item_filename_invoation = invocation
            directory.add_command_invocation(
                document_invocation, overwrite=True)
            directory.add_command_invocation(
                item_filename_invoation, overwrite=True, save=True)
        else:
            directory.add_command_invocation(
                invocation, overwrite=True, save=True)


if __name__ == "__main__":
    main()
