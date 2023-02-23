import os
from argparse import ArgumentParser

from mock_cli import ResponseDirectory, ResponseDirectoryException
from mock_cli.argv_conversion import arg_shlex_from_string

from .mock_op import MockOP


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--response-dir", help="Path to response directory JSON file")
    parser.add_argument(
        "--verbose", help="Include additional command response detail", action="store_true")

    parsed = parser.parse_args()
    return parsed


def print_command_verbose(response, command_string, response_dir):
    name = response["name"]
    out_path = os.path.join(response_dir, name, response["stdout"])
    err_path = os.path.join(response_dir, name, response["stderr"])
    exit_status = response["exit_status"]
    print(f"{command_string}")
    print(f"\toutput: {out_path}")
    print(f"\terror output: {err_path}")
    print(f"\texit status: {exit_status}")
    print("")


def main():
    parsed = parse_args()
    verbose = parsed.verbose
    if parsed.response_dir:
        respdir_json_file = parsed.response_dir
    else:
        respdir_json_file = MockOP()._response_directory

    try:
        directory = ResponseDirectory(respdir_json_file)
    except ResponseDirectoryException as e:
        print(f"Error loading response directory: {e}")
        exit(1)

    print(f"Directory path: {respdir_json_file}")
    commands = directory.commands
    response_dir = directory.response_dir
    commands_with_input = directory.commands_with_input

    for cmd, response in commands.items():
        cmd_string = arg_shlex_from_string(cmd, popped_args=['op'])
        if verbose:
            print_command_verbose(response, cmd_string, response_dir)
        else:
            print(f"{cmd_string}")

    for input_hash, input_dict in commands_with_input.items():
        print(f"For input hash: {input_hash}:")
        for cmd, response in input_dict.items():
            cmd_string = arg_shlex_from_string(cmd, popped_args=['op'])
        if verbose:
            print_command_verbose(response, cmd_string, response_dir)
        else:
            print(f"{cmd_string}")
