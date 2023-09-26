from configparser import ConfigParser
from typing import List


class OPConfigParser(ConfigParser):
    _key_types = {
        "enabled": "getboolean",
        "expected-return": "getint",
        "expected-return-2": "getint",
        "include-archive": "getboolean",
        "categories": "getcsvlist",
        "tags": "getcsvlist",
        "changes-state": "getboolean",
        "set-env-vars": "get_dict_from_csv",
        "pop-env-vars": "getcsvlist",
        "item-favorite": "getboolean",
        "state-iteration": "getint",
        "skip-global-signin": "getboolean",
        "create-instance": "getboolean",
        "append-tags": "getboolean"
    }

    def items(self, section):
        print("items")
        _items = super().items(section)
        d = dict()
        for k, v in _items:
            if k in self._key_types:
                v = self._key_types[k](v)
            d[k] = v
        return d.items()

    def get(self, section, option, *args, **kwargs):
        get_fn = super().get
        if option in self._key_types and 'raw' not in kwargs:
            fn_name = self._key_types[option]
            get_fn = getattr(self, fn_name)
            val = get_fn(section, option, *args, **kwargs)
        else:
            val = get_fn(section, option, *args, **kwargs)

        return val

    def getcsvlist(self, section, option, *args, **kwargs):
        val = super().get(section, option, *args, **kwargs)
        val_list = None
        if val:
            val_list = val.split(",")
        return val_list

    def get_dict_from_csv(self, section, option, *args, **kwargs):
        # turn a string like:
        # key_1:val_1,key_2:val2
        # into a dictionary
        csv_list = self.getcsvlist(section, option, *args, **kwargs)
        val_dict = None
        if csv_list:
            tuple_list = [tuple(val.split(":")) for val in csv_list]
            val_dict = dict(tuple_list)
        return val_dict


class OPresponseDefinition(dict):
    def __init__(self, section_name, section):
        super().__init__()
        resp_def = {"name": section_name}
        sect_dict = dict(section)
        resp_def.update(sect_dict)
        self.update(resp_def)

    @property
    def type(self) -> str:
        return self["type"]

    @property
    def enabled(self) -> bool:
        return self.get('enabled', True)


class OPResponseGenConfig(dict[str, OPresponseDefinition]):
    MAIN_SECTION = "MAIN"
    CONF_PATH_KEY = "config-path"
    RESP_PATH_KEY = "response-path"
    INPUT_PATH_KEY = "input-path"
    RESP_DIR_KEY = "response-dir-file"
    IGN_SIGNIN_FAIL_KEY = "ignore-signin-fail"
    EXISTING_AUTH_KEY = "existing-auth"
    STATE_CONF_KEY = "state-config"
    STATE_ITERATION_KEY = "state-iteration"
    SET_VARS_KEY = "set-env-vars"
    POP_VARS_KEY = "pop-env-vars"
    SKIP_GLOBAL_SIGNIN_KEY = "skip-global-signin"

    def __init__(self, config_path, definition_whitelist=[]):
        super().__init__()
        conf = OPConfigParser()
        conf.read(config_path)

        self.config_path = conf.get(self.MAIN_SECTION, self.CONF_PATH_KEY)
        self.response_path = conf.get(self.MAIN_SECTION, self.RESP_PATH_KEY)
        self.respdir_json_file = conf.get(self.MAIN_SECTION, self.RESP_DIR_KEY)
        self.ignore_signin_fail = conf.get(
            self.MAIN_SECTION, self.IGN_SIGNIN_FAIL_KEY, fallback=False)
        self.input_path = conf.get(
            self.MAIN_SECTION, self.INPUT_PATH_KEY, fallback=None)
        self.existing_auth = conf.get(
            self.MAIN_SECTION, self.EXISTING_AUTH_KEY, fallback="available")
        self.state_conf = conf.get(
            self.MAIN_SECTION, self.STATE_CONF_KEY, fallback=None)
        self.state_iteration = -1
        if self.state_conf:
            self.state_iteration = conf.get(
                self.MAIN_SECTION, self.STATE_ITERATION_KEY, fallback=0)
        self.set_env_vars = conf.get(
            self.MAIN_SECTION, self.SET_VARS_KEY, fallback=None)
        self.pop_env_vars = conf.get(
            self.MAIN_SECTION, self.POP_VARS_KEY, fallback=None)
        self.skip_global_signin = conf.get(
            self.MAIN_SECTION, self.SKIP_GLOBAL_SIGNIN_KEY, fallback=False)

        response_defs = self._get_response_defs(conf, definition_whitelist)
        self.update(response_defs)

    def _get_response_defs(self, conf: OPConfigParser, whitelist: List[str]):
        response_defs = {}
        for sname in conf.sections():
            if sname != self.MAIN_SECTION:
                if whitelist and sname not in whitelist:
                    continue
                sect = conf[sname]
                resp_def = OPresponseDefinition(sname, sect)
                response_defs[sname] = resp_def
        for definition in whitelist:
            if definition not in response_defs:
                raise Exception(
                    f"Whitelisted definition not found: {definition}")

        return response_defs

    @property
    def sections(self) -> List[str]:
        return self.keys()
