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

- It often needs to be run interactively to authenticate
- Cases where authentication can be performed programatically may require storing 1Password account credentials insecurely
- An actual, paid 1Password account must exist and contain data
  - This would need to be a test account in order to avoid exposing sensitive passwords, etc. and to share the account across an engineering team, which may be impractical
- Internet connectivity is required
- The time required for `op` to execute a single query and return a response may be impractical, particularly in a testing environment with very many test cases

The first few problems are (mostly) addressed by the recent addition of 1Password service accounts which allow querying of a vault without storing passwords. However you still need to keep the service account token, which itself is potentially sensitive, someplace probably not in version control. Then there's still the requirement for network connectivity and the performance of hitting 1Password.com for potentially hundreds or thousands of tests.

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

To have `mock-op` use this configuration, set the `MOCK_OP_RESPONSE_DIRECTORY` environment variable to the response directory JSON file's path:

```shell
export MOCK_OP_RESPONSE_DIRECTORY=tests/config/mock-op/response-directory.json
```

With that directory in place, the `mock-op` utility will look up responses and exit status based on the set of command-line arguments given:

```Console
$ mock-op item get nok7367v4vbsfgg2fczwu4ei44 --fields username,password
{"password":"weak password","username":"janedoe123"}
$ mock-op item get "Invalid Item"
[ERROR] 2021/02/03 13:39:42 "Invalid Item" doesn't seem to be an item. Specify
the item with its UUID, name, or domain.
$ echo $?
1
$
```

## Automated Response Generation

The response file & directory structure was designed to be fairly straightforward so that one could create it by hand or easily script it. However, `mock-op` comes with a tool to generate responses. You provide it a configuration file, and it will connect to your 1Password account (using the *real* `op` tool), perform the queries, and record the responses.

> Note: response generation requires you install the `pyonepassword` Python package. It's resopnsible for driving the `op` command under the hood so its responses can be captured.
>
> It's only required during response generation, and is *not* required for subsequent use of `mock-op`.
>
> It can be found in PyPI and installed via: `pip3 install pyonepassword`.

Here's an example configuraiton file for generating responses. Note that the invalid item definition has an `expected-return` value of 1. This tells `response-generator` that an error is expected and should be captured rather than failing.

```INI
[MAIN]
config-path = ./tests/config/mock-op
response-path = responses
response-dir-file = response-directory.json

[whoami]
type=whoami

[item-get-example-login-1-vault-test-data]
type=item-get
item_identifier = Example Login 1
vault = Test Data

[item-get-invalid]
type = item-get
item_identifier = Invalid Item
expected-return = 1
```

Then you can run `response-generator` and have it create your response directory:

```Console
❱ response-generator ./examples/example-response-generation.cfg
Running: op --version
Running: op --format json account list
Running: op --format json whoami
Running: op signin --raw
Running: op --format json whoami
Signed in as User ID: *********************ERLHI
About to run: op --format json whoami
About to run: op --format json item get 'Example Login 1' --vault 'Test Data'
About to run: op --format json item get 'Invalid Item'
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
$  list-cmds --response-dir ./tests/config/mock-op/response-directory.json
Directory path: ./tests/config/mock-op/response-directory.json
op --format json whoami
op --format json item get 'Example Login 1' --vault 'Test Data'
op --format json item get 'Invalid Item'
```

List all simulated `op` commands with response context:

```Console
❱ list-cmds --response-dir ./tests/config/mock-op/response-directory.json --verbose
Directory path: ./tests/config/mock-op/response-directory.json
op --format json whoami
	output: tests/config/mock-op/responses/whoami/output
	error output: tests/config/mock-op/responses/whoami/error_output
	exit status: 0

op --format json item get 'Example Login 1' --vault 'Test Data'
	output: tests/config/mock-op/responses/item-get-example-login-1-vault-test-data/output
	error output: tests/config/mock-op/responses/item-get-example-login-1-vault-test-data/error_output
	exit status: 0

op --format json item get 'Invalid Item'
	output: tests/config/mock-op/responses/item-get-invalid/output
	error output: tests/config/mock-op/responses/item-get-invalid/error_output
	exit status: 1
```
