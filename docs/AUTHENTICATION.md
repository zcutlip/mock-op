# MOCK-OP

## Authentication

### Simulating Authentication Scenarios

`mock-op` can't simulate actual authentication. For example, it can't know the difference between a correct or incorrect master password. And it can't prompt for biometric authentication, etc.

It is also not possible for `mock-op` to "know" if it has been authenticated during subsequent operations. So you can't make `op item get` fail as a result of `op signin` failing.

However, it can simulate the *results* of a few authentication scenarios. This enables you to test your code's logic for handling successful and unsuccessful `op signin` operations.

#### Authentication Success

To simulate successful sign-in without connection to the 1Password app set the following environment variables:
- `MOCK_OP_SIGNIN_SUCCEED=1`
- `MOCK_OP_SIGNIN_USES_BIO=0`

This will generate a fake session token along with the same shell text `op` produces when running `eval $(op signin)`:

```console
❱ export MOCK_OP_SIGNIN_USES_BIO=1
❱ export MOCK_OP_SIGNIN_SUCCEED=0
❱ mock-op --account testuser signin
export OP_SESSION_testuser="nfC2Fuv8PbtD5sy5ytzH0wFhrzCsbAes7poAoe4XsKt"
# This command is meant to be used with your shell's eval function.
# Run 'eval $(op signin testuser)' to sign in to your 1Password account.
# Use the --raw flag to only output the session token.
```

To simulate the same but with the 1Password app connection enabled, set `MOCK_OP_SIGNIN_USES_BIO=1`. Much like with `op signin` with biometric authentication, this will result in a successful exit status with zero output:

```console
❱ export MOCK_OP_SIGNIN_USES_BIO=1
❱ export MOCK_OP_SIGNIN_SUCCEED=0
❱ mock-op signin  # no output is generated but $? is 0
❱ echo $?
0
```

#### Authentication Failure

To simulate authentication failure, set `MOCK_OP_SIGNIN_SUCCEED=0`. This will result in an unsuccessful exit status as well as an error message logged to `stderr` just as `op` does.

```console
❱ export MOCK_OP_SIGNIN_SUCCEED=0
❱ mock-op signin
[ERROR] 2023/06/15 15:21:21 Authentication: DB: 401: Unauthorized
```


### Service Accounts

There isn't really anything to simulate for `mock-op` related to service accounts since signing in with `op` isn't required. You just set the environment variable and perform the query.

However, if you want to use a service account to generate responses so you don't have to authenticate, that is supported, and is very straightforward. You can do it in one of two ways.

1. Set your `OP_SERVICE_ACCOUNT_TOKEN` environment variable ahead of time before running `response-generator`.
2. Use a `.env` file and `response-generator` will load it. It defaults to `.env` in the current working directory, or you can set `RESP_GEN_DOT_ENV_FILE` to the path of a file to load:

```console
❱ export RESP_GEN_DOT_ENV_FILE=path/to/test/config/svc_acct_env
❱ response-generator ./tests/config/response-generation.cfg
```

If the service account token isn't set for some reason, you may want to ensure `op` fails, rather than prompts for authentication. Add the `existing-auth = required` option to your configuration file's `DEFAULT` section:

```ini
[MAIN]
config-path = ./tests/config/mock-op
response-path = responses-svc-acct
response-dir-file = svc-acct-response-directory.json
# existing-auth required results in hard failure if there's
# no existing authentication
existing-auth = required
```
