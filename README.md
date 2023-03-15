# MOCK-OP

## Summary

`mock-op` is a utility to stand-in for 1Password's `op` command-line utlity in scenarios such as automated testing.

## Description

The `mock-op` package comes with several significant parts:

- A `mock-op` console utility that plays back responses identical the real `op` command's output for a given set of command-line arguments. Additionally the same exit statuses are returned in the case of error.
- A `response-generator` console utility that executes `op` under various scenarios and records its responses for use by `mock-op`
- A utility to list `op` invocation argument lists known by the response directory

## Motivation

The reason for a "mock-op" that simulates the real `op` is primarily for the automated testing of scripts or other programs that shell out to the `op` command in order to query 1Password cloud accounts. The real `op` is potentially unsuitable for automated testing for a variety of reasons:

- It usually needs to be run interactively to authenticate
- Cases where authentication can be performed programatically may require storing 1Password account credentials insecurely
- An actual, paid 1Password account must exist and contain data
  - This would need to be a test account in order to avoid exposing sensitive passwords, etc. and to share the account across an engineering team, which may be impractical
- The time required for `op` to execute a single query and return a response may be impractical, particularly in a testing environment with very many test cases
- It's generally preferred to keep test data corpus in version control, which isn't possible when testing against a live 1Password account

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

The response file & directory structure was designed to be fairly straightforward so that one could create it by hand or easily script it. However, `mock-op` comes with a tool to generate responses. You provide it a configuration file, and it'll sign in to your 1Password account (using the *real* `op` tool), perform the queries, and record the responses.

> Note: response generation requires you install the `pyonepassword` Python package, which is not explicitly installed with `mock-op`. It can be found in PyPI and installed via `pip`. After responses have been generated, it's no longer required for `mock-op` operation. `mock-op` can be added and and used as a test dependency in your project without pulling in `pyonepassword`.

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
; this query is expected to fail
; expected-return = 1 is required
type = item-get
item_identifier = Invalid Item
expected-return = 1

[document-get-spongebob-image]
; this performs two operations and generates two responses
; one for 'op item get <document identifier> to get the filename
; a second for 'op document get <document identifier> to get the actual document bytes
type = document-get
vault=Test Data
item_identifier = Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp
```

Then you can run `response-generator` and have it create your response directory:

```Console
❱ response-generator ./response-generation.cfg
1Password master password:

Using account shorthand found in op config: my_onepassword_login
Doing normal (non-initial) 1Password sign-in
...
❱ tree tests/config/mock-op
tests/config/mock-op
├── response-directory.json
└── responses
    ├── document-get-spongebob-image
    │   ├── error_output
    │   └── output
    ├── document-get-spongebob-image-filename
    │   ├── error_output
    │   └── output
    ├── item-get-example-login-1-vault-test-data
    │   ├── error_output
    │   └── output
    └── item-get-invalid
        ├── error_output
        └── output

6 directories, 9 files

❱ file tests/config/mock-op/responses/document-get-spongebob-image/output
tests/config/mock-op/responses/document-get-spongebob-image/output: RIFF (little-endian) data, Web/P image
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
op item get 'Example Login 1' --vault 'Test Data'
op item get nok7367v4vbsfgg2fczwu4ei44
op item get nok7367v4vbsfgg2fczwu4ei44 --fields username,password
op document get 'Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp'
op item get 'Invalid Item'
```

List all simulated `op` commands with response context (and alternate directory location):

```Console
$ list-cmds --response-dir ./response-directory.json --verbose
Directory path: ./response-directory.json
./responses
op item get 'Example Login 1' --vault 'Test Data'
	output: ./responses/item-get-[example-login-1]-[vault-test-data]/output
	error output: ./responses/item-get-[example-login-1]-[vault-test-data]/error_output
	exit status: 0

op item get nok7367v4vbsfgg2fczwu4ei44
	output: ./responses/item-get-by-uuid[example-login-1]/output
	error output: ./responses/item-get-by-uuid[example-login-1]/error_output
	exit status: 0

op item get nok7367v4vbsfgg2fczwu4ei44 --fields username,password
	output: ./responses/item-get-[example-login-2]-[fields-username-password]/output
	error output: ./responses/item-get-[example-login-2]-[fields-username-password]/error_output
	exit status: 0

op document get 'Example Login 2 - 1200px-SpongeBob_SquarePants_character.svg.png.webp'
	output: ./responses/document-get-[spongebob image]/output
	error output: ./responses/document-get-[spongebob image]/error_output
	exit status: 0

op item get 'Invalid Item'
	output: ./responses/item-get-[invalid-item]/output
	error output: ./responses/item-get-[invalid-item]/error_output
	exit status: 1
```
