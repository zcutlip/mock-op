# MOCK-OP

## Environment Variables Affecting mock-op's Behavior

The following is a list of environment variables that determine `mock-op`'s and `response-generator`'s behavior

### mock-op

- `MOCK_OP_RESPONSE_DIRECTORY`: The path to the response directory JSON file that `mock-op` should use
  - Mutually exclusivie with `MOCK_OP_STATE_DIR`
- `MOCK_OP_STATE_DIR`: The path to the state configuration file `mock-op` should used if state-changing operations are required
  - Mutually exclusive with `MOCK_OP_RESPONSE_DIRECTORY`
  - This file will be modified, so a temporary copy should be used if it is version controlled
- `MOCK_OP_SIGNIN_USES_BIO`: `0` or `1` indicating how `mock-op signin` should behave
  - `0` indicates successful `signin` should generate output similar to `op`'s session token output
  - `1` indicates successful `signin` should generate no output
- `MOCK_OP_SIGNIN_SUCCEED`: `0` or `1` indicating whether to emulate `signin` success or failure & exit status
  - Failure will generate error output similar to that of `op`'s error output when sign-in fails
  - Success will generate output as appropriate per the `MOCK_OP_SIGNIN_USES_BIO` setting
- `MOCK_OP_SIGNIN_ACCOUNT`: The account identifier `mock-op` should emulate signing in with
  - `op` can sign into an account either specified by `--account` or using the most recently used account
  - `mock-op` emulates `op`'s implicit account selection using this environment variable

### response-generator

If a 1Password service account is desired when generating responses, `response-generator` supports two ways of setting the token:

- `OP_SERVICE_ACCOUNT_TOKEN`: Service account token `op` should use when generating responses
- `RESP_GEN_DOT_ENV_FILE`: A dot-env file (e.g., `.env_secret`) `response-generator` should load
  - This is the recommended way of setting a service account token, rather than setting the environment variable directly
