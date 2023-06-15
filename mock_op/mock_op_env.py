import os
import pathlib

from dotenv import load_dotenv

RESP_GEN_DOT_ENV_VAR_NAME = "RESP_GEN_DOT_ENV_FILE"
MOCK_OP_DOT_ENV_VAR_NAME = "MOCK_OP_DOT_ENV_FILE"


def _load_dot_env(ENV_VAR_NAME: str):
    dot_env_file = os.environ.get(ENV_VAR_NAME)
    if not dot_env_file:
        dot_env_file = ".env"
    dot_env_path = pathlib.Path(dot_env_file)
    if dot_env_path.exists():
        load_dotenv(dot_env_path)


def resp_gen_load_dot_env():
    _load_dot_env(RESP_GEN_DOT_ENV_VAR_NAME)


def mock_op_load_dot_env():
    _load_dot_env(MOCK_OP_DOT_ENV_VAR_NAME)
