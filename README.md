# MOCK-OP

## Summary

`mock-op` is a utility to stand-in for 1Password's `op` command-line utlity in scenarios such as automated testing.

## Description

The `mock-op` package comes with two significant parts:

- A `mock-op` console utility that plays back responses identical the real `op` command's output for a given set of command-line arguments. Additionally the same exit statuses are return in the case of error.
- An API that can be used to execute `op` under various scenarios and record its responses for use by `mock-op`

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
    "get|item|Example Login 1|--vault|Test Data": {
      "exit_status": 0,
      "stdout": "output",
      "stderr": "error_output",
      "name": "get-item-[example-login-1]-[vault-test-data]"
    },
    "get|item|nok7367v4vbsfgg2fczwu4ei44|--fields|username,password": {
      "exit_status": 0,
      "stdout": "output",
      "stderr": "error_output",
      "name": "get-item-[example-login-2]-[fields-username-password]"
    },
    "get|item|Invalid Item": {
      "exit_status": 1,
      "stdout": "output",
      "stderr": "error_output",
      "name": "get-item-[invalid-item]"
    }
  }
}

```

And an on-disk repository of response files:

```
responses
├── get-item-[example-login-1]-[vault-test-data]
│   ├── error_output
│   └── output
├── get-item-[example-login-2]-[fields-username-password]
│   ├── error_output
│   └── output
└── get-item-[invalid-item]
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
