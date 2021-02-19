import getpass

from argparse import ArgumentParser
from pathlib import Path

from mock_cli import CommandInvocation, ResponseDirectory

from .response_generator import OPResponseGenerator
from .response_generator_config import OPResponseGenConfig


def resp_gen_parse_args():
    parser = ArgumentParser()
    parser.add_argument("config", help="Config file describing 'op' responses to generate")

    parsed = parser.parse_args()
    return parsed


def do_signin():
    # If you've already signed in at least once, you don't need to provide all
    # account details on future sign-ins. Just master password
    my_password = getpass.getpass(prompt="1Password master password:\n")
    # You may optionally provide an account shorthand if you used a custom one during initial sign-in
    # shorthand = "arbitrary_account_shorthand"
    # return OP(account_shorthand=shorthand, password=my_password)
    # Or we'll try to look up account shorthand from your latest sign-in in op's config file
    return OPResponseGenerator(password=my_password)


def do_get_item(op: OPResponseGenerator, query_name, query_definition) -> CommandInvocation:
    item_id = query_definition["item_identifier"]
    vault = query_definition.get("vault")
    invocation = op.get_item_generate_response(item_id, query_name, vault=vault)
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
        # exit(1)
    directory = ResponseDirectory(
        respdir_json_file, create=True, response_dir=response_path)

    for query_name, query_definition in generator_config.items():
        if query_definition["type"] == "get-item":
            invocation = do_get_item(op, query_name, query_definition)
        else:
            raise Exception(f"Unknown query type: {query_definition['type']}")

        directory.add_command_invocation(invocation, overwrite=True, save=True)


if __name__ == "__main__":
    main()
