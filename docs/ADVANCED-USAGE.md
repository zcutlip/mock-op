# MOCK-OP

## Advanced Usage

### Input from Standard In

Some of `op`'s commands read input from `stdin`. In these cases, it isn't sufficient for `mock-op`[^1] to look up a response solely based on the command line arguments provided. For a given set of arguments, the response may be drastically different for one input than for another.

The way `mock-op` handles this is to check `stdin` for data. If there is input data, an md5 digest is computed. Then the response is looked up first based on the md5 hash as well as the command line argument list.

For example, `op item delete` can take a JSON-encoded list of items to delete over `stdin`. In this case mock-op hashes the input if there is any, and looks up the response under a `commands_with_input` subdictionary. An example `response-directory.json` might look like:

```JSON
{
  "meta": {
    "response_dir": "tests/config/mock-op/responses-with-input",
    "input_dir": "input"
  },
  "commands": {
    "--format|json|whoami": {
      "exit_status": 0,
      "stdout": "output",
      "stderr": "error_output",
      "name": "whoami",
      "changes_state": false
    },
  "commands_with_input": {
    "fc4bcec96b5abaca5effb19e02d128a3": {
      "--format|json|item|delete|-|--vault|Test Data 3": {
        "exit_status": 0,
        "stdout": "output",
        "stderr": "error_output",
        "name": "item-batch-delete-tag-1_part_000",
        "changes_state": false
      }
    }
}

```

The response directory above shows the normal `commands` subdictionary, in addition to the `commands_with_input` dictionary. So if one were to simulate deleting a batch of items, you would:
- Start with a JSON list hashing to the appropriate entry above (fc4bcec96b5abaca5effb19e02d128a3 in this case)
- Pipe the JSON list to `mock-op`
- Provide the arguments to `mock-op`: `--format json item delete - --vault "Test Data 3"`

And `mock-op` would first look up any responses that matched the provided input, and then find the appropriate response based on the provided command line arguments.

As described in the README, the intent of this design is that it should be relatively easy to construct a response directory with whatever tooling and/or scripting the user desires. However, `response-generator` will handle input-hashing scenarios transparently for `mock-op` commands that need it.

### State-Changing Operations

#### Stateful Response Directory

Some testing scenarios require operations that mutate the state of 1Password data. For example, consider testing the following:

- List all items in vault "Test Data" with tag "tag_3"
  - Verify the list is not empty
- Delete all items in vault "Test Data" with tag "tag_3"
- Again list all items in vault "Test Data" with tag "tag_3"
  - Verify the list is empty this time

As we know, `mock-op` doesn't touch or interact with real 1Password data. It also doesn't alter your response directory, since that's expected to be version controlled test configuration. So the way this is handled is for each state the input data should have, a separate response directory is provided. Whenever a command would mutate the 1Password data, `mock-op` will know to iterate its list of response directories for the next query.

In the above use case involving a listing, a deletion, and a second listing, you would have a starting state and then an ending state post-deletion.

There is a special configuration file, in addition to `response-directory.json`, that tells `mock-op` how and when to iterate and where to find its data each time. For example:

```JSON
{
  "iteration": 0,
  "max-iterations": 2,
  "state-list": [
    {
      "response-directory": "tests/config/mock-op/responses/item-delete-multiple/response-directory-1.json",
      "env-vars": {
        "set": {},
        "pop": []
      }
    },
    {
      "response-directory": "tests/config/mock-op/responses/item-delete-multiple/response-directory-2.json",
      "env-vars": {
        "set": {},
        "pop": []
      }
    }
  ]
}
```

Let's walk through this configuration:

- `iteration`: This should be set to 0. `mock-op` will increment it after each state change
- `max-iterations`: An exception will be raised if the number of state changes equals or exceeds this number
- `state-list`: A list of state configurations to be used, one for each stage change

  Each individual state configuration consists of:

  - `response-directory`: The path to the response directory JSON file for this state
  - `env-vars`: Any environment variables that should be unset (a list of names), or set (a dictionary of names & values) for each state.

Assuming the above stateful configuration, to have `mock-op` use it, set the `MOCK_OP_STATE_DIR` environment variable to the path to state configuration file, e.g.,

```shell
export MOCK_OP_STATE_DIR=tests/config/mock-op/mock-op-state-config.json
```

> *Note 1:* `mock-op` modifies the state the state configuration file at each iteration. Since it will likely be added to version control, it is advised to make a temporary copy for use during testing.

> *Note 2:* When using a stateful configuraiton, it's important to *not set* the `MOCK_OP_RESPONSE_DIRECTORY` environment variable. Having both variables set will be an error.


Again, this is intended to be relatively straightforward to hand-craft or to script. However `response-generator` can create it automatically.

The following sample `response-generator` configuration causes a state change configuration to be generated:

```ini
[MAIN]
config-path = ./tests/config/mock-op/responses/item-delete-multiple
response-path = responses-1
input-path = input
response-dir-file = response-directory-1.json
state-config = ./tests/config/mock-op/responses/item-delete-multiple/mock-op-state-config-1.json


[item-batch-delete-tag-1]
type = item-delete-multiple
tags = tag_1
vault = Test Data 3
changes_state = true
```

[^1]: Currently the only command `mock-op` emulates where this applies is `item delete`, but other command will be added as needed.
