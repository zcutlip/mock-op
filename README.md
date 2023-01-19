# MOCK-OP

## Summary

`mock-op` is a utility to stand-in for 1Password's `op` command-line utlity in scenarios such as automated testing.

## Description

The `mock-op` package comes with several significant parts:

- A `mock-op` console utility that plays back responses identical the real `op` command's output for a given set of command-line arguments. Additionally the same exit statuses are returned in the case of error.
- An API that can be used to execute `op` under various scenarios and record its responses for use by `mock-op`
- An API to implement a custom `mock-op` console utility overriding the defaults, such as providing a custom argument parser
- A utility to list `op` invocation argument lists known by the response directory

## Motivation

The reason for a "mock-op" that simulates the real `op` is primarily for the automated testing of scripts or other programs that shell out to the `op` command in order to query 1Password cloud accounts. The real `op` is potentially unsuitable for automated testing for a variety of reasons:

- It usually needs to be run interactively to authenticate
- Cases where authentication can be performed programatically may require storing 1Password account credentials insecurely
- An actual, paid 1Password account must exist and contain data
  - This would need to be a test account in order to avoid exposing sensitive passwords, etc. and to share the account across an engineering team, which may be impractical
- The time required for `op` to execute a single query and return a response may be impractical, particularly in a testing environment with very many test cases

## Usage

### `mock-op` CLI Tool

In order for `mock-op` to simulate the real `op` it needs a directory of responses to look up and play back. The anatomy of the response directory is discussed in the README for [`mock-cli-framework`](https://github.com/zcutlip/mock-cli-framework), but below is an example:

JSON Dictionary of command invocations:

```JSON
{
  "meta": {
    "response_dir": "./responses"
  },
  "commands": {
    "item|get|Example Login 1|--vault|Test Data": {
      "exit_status": 0,
      "stdout": "output",
      "stderr": "error_output",
      "name": "item-get-[example-login-1]-[vault-test-data]"
    },
    "item|get|nok7367v4vbsfgg2fczwu4ei44|--fields|username,password": {
      "exit_status": 0,
      "stdout": "output",
      "stderr": "error_output",
      "name": "item-get-[example-login-2]-[fields-username-password]"
    },
    "item|get|Invalid Item": {
      "exit_status": 1,
      "stdout": "output",
      "stderr": "error_output",
      "name": "item-get-[invalid-item]"
    }
  }
}

```

And an on-disk repository of response files:

```
responses
├── item-get-[example-login-1]-[vault-test-data]
│   ├── error_output
│   └── output
├── item-get-[example-login-2]-[fields-username-password]
│   ├── error_output
│   └── output
└── item-get-[invalid-item]
    ├── error_output
    └── output
```

With that directory in place, the `mock-op` utility will look up responses and exit status based on the set of command-line arguments given:

```Console
$ mock-op get item nok7367v4vbsfgg2fczwu4ei44 --fields username,password
{"password":"weak password","username":"janedoe123"}
$ mock-op get item "Invalid Item"
[ERROR] 2021/02/03 13:39:42 "Invalid Item" doesn't seem to be an item. Specify
the item with its UUID, name, or domain.
$ echo $?
1
$
```

## Automated Response Generation

The response file & directory structure was designed to be fairly straightforward so that one could create it by hand or easily script it. However, `mock-op` comes with a tool to generate responses. You provide it a configuration file, and it'll sign in to your 1Password account (using the *real* `op` tool), perform the queries, and record the responses.

> Note: response generation requires you install my `pyonepassword` Python package. It can be found in PyPI and installed via `pip`.

Here's an example configuraiton file for generating responses:

```INI
[DEFAULT]
config-path = ./tests/config/mock-op
response-path = responses
response-dir-file = response-directory.json

[item-get-example-login-1-vault-test-data]
type=item-get
item_identifier = Example Login 1
vault = Test Data

[item-get-invalid]
type = item-get
item_identifier = Invalid Item
```

Then you can run `response-generator` and have it create your response directory:

```Console
response-generator ./response-generation.cfg
1Password master password:

Using account shorthand found in op config: my_onepassword_login
Doing normal (non-initial) 1Password sign-in
```

## Using the OP Response Generation API

In addition, `mock-op` provides API to execute `op` and record its responses. In order to do this, the `pyonepassword` package is required, and is not automatically installed as a dependency of this package:

    pip install pyonepassword


> Note: As the response generation API uses `pyonepassword` under the hood, it is limited to `op` commands and subcommands that `pyonepassword` knows about.


Then generate and record responses in the following order:

1. Obtain master password for the 1Password account
2. Create an OPResponseGenerator object, which signs in to a real 1Password account (whichever account `op` has signed into previously on the command line)
3. Create a `ResponseDirectory` instance
4. Generate a command invocation for either the `op get item` or `op get document` subcommand
5. Add the command invocation (a bundle of the command-line arguments, the response output, and the exit status) to the response directory

> Note: Although generating the command invocation communicates to the live 1Password account, it will not raise exceptions if the `op` query fails. The invocation captures context describing the success or failure.

There is a detailed example in the `examples/` directory, but here is an abbreviated one:

```Python
def do_signin():
    # Be sure to complete initial sign-in manually with the op command

    # Subsequent sign-ins only require master password
    my_password = getpass.getpass(prompt="1Password master password:\n")
    # You may optionally provide an account shorthand if you used a custom one during initial sign-in
    # shorthand = "arbitrary_account_shorthand"
    # return OPResponseGenerator(account_shorthand=shorthand, password=my_password)
    # Or we'll try to look up account shorthand from your latest sign-in in op's config file
    return OPResponseGenerator(password=my_password)

def do_document_get(op: OPResponseGenerator):
    document_name = "Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp"

    # Arbitrary but descriptive name
    query_name = "document-get-[spongebob image]"
    invocation: CommandInvocation = op.document_get_generate_response(document_name, query_name)
    return invocation

def do_item_get_invalid(op: OPResponseGenerator):
    item_name = "Invalid Item"

    # Arbitrary but descriptive name
    query_name = "item-get-[invalid-item]"
    invocation: CommandInvocation = op.item_get_generate_response(item_name, query_name)
    return invocation

def main():
    op = do_signin()
    respdir_json_file = "~/.config/mock-op/response-directory.json"
    resopnse_dir = "~/.config/mock-op/responses"

    # Create the directory on disk if it doesn't already exist
    directory = ResponseDirectory(respdir_json_file, create=True, response_dir=response_dir)


    invocation = do_document_get(op)
    # add the invocation to the directory, saving the updated directory to disk
    directory.add_command_invocation(invocation, save=True)

    invocation = do_item_get_invalid(op)
    directory.add_command_invocation(invocation, save=True)

```

This should create the response directory JSON file and directory structure descibed above. The `mock-op` utility may now play back `op` responses as if it was the real thing.

## Implementing a Custom `mock-op`

The `MockOP` class does most of the work emulating `op`. In the simplest case it may be instantiated in a simple `main()` and told to respond to the given command-line arguments. It will then sanity-check the arguments using its internal argument parser, and respond using the response directory found in `~/.config/mock-op/`. This is what the provided `mock-op` tool does.

It can also be instatiated with a custom argument parser as well as a custom path to the response directory. It can be extended to further customize behavior.

```Python

def mock_op_main():
    response_directory = "~/path/to/custom-directory.json"
    parser = get_custom_arg_parser()
    mock_op_cmd = MockOP(arg_parser=parser, response_directory=response_directory)

    # Parse args to fail on unknown args
    # This step may be skipped if it is not desired to sanity check arguments
    # A parsed argument object is returned in case the caller needs it, but
    # it is not required during the respond() step
    parsed = mock_op_cmd.parse_args()

    # We don't need argv[0], just arguments not including the program name
    args = sys.argv[1:]
    try:
        # output is written to standard out & standard err as appropriate
        # a numeric exit status is returned
        exit_status = mock_op_cmd.respond(args)
    except (ResponseDirectoryException, ResponseLookupException) as e:
        # Response directory failed to load, or did not contain an appropriate response
        print(f"Error looking up response: [{e}]", file=sys.stderr)
        exit_status = -1

    return exit_status

if __name__ == "__main__":
    exit(mock_op_main())
```

## Listing known `op` invocations

A convenience utlitity is provided to list invocation information known by the response directory.

    usage: list-cmds [-h] [--response-dir RESPONSE_DIR] [--verbose]

    optional arguments:
      -h, --help            show this help message and exit
      --response-dir RESPONSE_DIR
                            Path to response directory JSON file
      --verbose             Include additional command response detail

List all simulated `op` commands:

```Console
$ list-cmds
Directory path: ~/.config/mock-op/response-directory.json
op get item 'Example Login 1' --vault 'Test Data'
op get item nok7367v4vbsfgg2fczwu4ei44
op get item nok7367v4vbsfgg2fczwu4ei44 --fields username,password
op get document 'Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp'
op get item 'Invalid Item'
```

List all simulated `op` commands with response context (and alternate directory location):

```Console
$ list-cmds --response-dir ./response-directory.json --verbose
Directory path: ./response-directory.json
./responses
op get item 'Example Login 1' --vault 'Test Data'
	output: ./responses/item-get-[example-login-1]-[vault-test-data]/output
	error output: ./responses/item-get-[example-login-1]-[vault-test-data]/error_output
	exit status: 0

op get item nok7367v4vbsfgg2fczwu4ei44
	output: ./responses/item-get-by-uuid[example-login-1]/output
	error output: ./responses/item-get-by-uuid[example-login-1]/error_output
	exit status: 0

op get item nok7367v4vbsfgg2fczwu4ei44 --fields username,password
	output: ./responses/item-get-[example-login-2]-[fields-username-password]/output
	error output: ./responses/item-get-[example-login-2]-[fields-username-password]/error_output
	exit status: 0

op get document 'Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp'
	output: ./responses/document-get-[spongebob image]/output
	error output: ./responses/document-get-[spongebob image]/error_output
	exit status: 0

op get item 'Invalid Item'
	output: ./responses/item-get-[invalid-item]/output
	error output: ./responses/item-get-[invalid-item]/error_output
	exit status: 1
```
