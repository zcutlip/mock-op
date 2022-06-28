import getpass
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from mock_cli import CommandInvocation, ResponseDirectory

from ._op import OPNotSignedInException, OPSigninException
from .response_generator import OPResponseGenerator
from .response_generator_config import OPResponseGenConfig


DEFAULT_CONFIG_PATH = Path(".", "response-generation.cfg")


def resp_gen_parse_args():

    def split_args(arg_string: str) -> List[str]:
        # Be sure to strip, maybe they have spaces where they don't belong and wrapped the arg value in quotes
        csv_list = [v.strip() for v in arg_string.split(",")]
        return csv_list

    parser = ArgumentParser()
    parser.add_argument(
        "config", help="Config file describing 'op' responses to generate. defaults to './response-generation.cfg", nargs="?")
    parser.add_argument(
        "-D", "--definition", help="Only run the specified query definition",
        type=split_args
    )

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


def item_get_totp(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    item_id = query_definition["item_identifier"]
    vault = query_definition.get("vault")
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.item_get_generate_response(
        item_id, query_name, vault=vault, expected_ret=expected_return, fields="type=otp")
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


def vault_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    group_id = query_definition.get("group_identifier", None)
    user_id = query_definition.get("user_identifier", None)

    invocation = op.vault_list_generate_response(
        query_name, group_name_or_id=group_id, user_name_or_id=user_id, expected_ret=expected_return)
    return invocation


def user_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    user_id = query_definition["user_identifier"]
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.user_get_generate_response(
        user_id, query_name, expected_ret=expected_return)
    return invocation


def user_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    group_id = query_definition.get("group_identifier", None)
    vault = query_definition.get("vault", None)
    invocation = op.user_list_generate_response(
        query_name, group_name_or_id=group_id, vault=vault, expected_ret=expected_return)
    return invocation


def group_get(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    group_id = query_definition["group_identifier"]
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.group_get_generate_response(
        group_id, query_name, expected_ret=expected_return)
    return invocation


def group_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    user_id = query_definition.get("user_identifier", None)
    vault = query_definition.get("vault", None)
    invocation = op.group_list_generate_response(
        query_name, user_name_or_id=user_id, vault=vault, expected_ret=expected_return)
    return invocation


def do_cli_version(op: OPResponseGenerator, query_name, _unused_query_definition) -> CommandInvocation:
    invocation = op.cli_version(query_name)
    return invocation


def item_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    categories = query_definition.get("categories", [])
    include_archive = query_definition.get("include_archive", False)
    tags = query_definition.get("tags", [])
    vault = query_definition.get("vault", None)

    invocation = op.item_list_generate_response(
        query_name, categories=categories, include_archive=include_archive,
        tags=tags, vault=vault, expected_ret=expected_return)

    return invocation


def item_template_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.item_template_list_generate_response(
        query_name, expected_ret=expected_return)

    return invocation


def account_list(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    expected_return = query_definition.get("expected-return", 0)
    invocation = op.account_list_generate_response(
        query_name, expected_ret=expected_return)
    return invocation


query_type_map = {
    "item-get": item_get,
    "item-get-totp": item_get_totp,
    "document-get": document_get,
    "vault-get": vault_get,
    "vault-list": vault_list,
    "user-get": user_get,
    "user-list": user_list,
    "group-get": group_get,
    "group-list": group_list,
    "cli-version": do_cli_version,
    "item-list": item_list,
    "account-list": account_list,
    "item-template-list": item_template_list
}


def signin_fail(excaption: Exception):
    print(str(excaption))
    exit(1)


def main():
    args = resp_gen_parse_args()
    conf_path = args.config
    if not conf_path:
        conf_path = DEFAULT_CONFIG_PATH

    definition_list = []
    if args.definition:
        definition_list = args.definition
    generator_config = OPResponseGenConfig(
        conf_path, definition_whitelist=definition_list)
    config_dir = Path(generator_config.config_path).expanduser()

    respdir_json_file = Path(
        config_dir, generator_config.respdir_json_file)
    response_path = Path(config_dir, generator_config.response_path)

    try:
        op = do_signin()
    except OPSigninException as e:
        if generator_config.ignore_signin_fail:
            # some actions only require class methods and don't require sign-in success
            # if this blows up on other actions that's our fault for setting the env variable
            op = OPResponseGenerator
        else:
            signin_fail(e)
    except Exception as e:
        signin_fail(e)

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
