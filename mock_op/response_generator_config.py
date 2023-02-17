from configparser import ConfigParser
from typing import List


class OPConfigParser(ConfigParser):
    _key_types = {
        "enabled": "getboolean",
        "expected-return": "getint",
        "expected-return-2": "getint",
        "include-archive": "getboolean",
        "categories": "getcsvlist",
        "tags": "getcsvlist"
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
        val_list = val.split(",")
        return val_list


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
    CONF_PATH_KEY = "config-path"
    RESP_PATH_KEY = "response-path"
    INPUT_PATH_KEY = "input-path"
    RESP_DIR_KEY = "response-dir-file"
    IGN_SIGNIN_FAIL_KEY = "ignore-signin-fail"

    def __init__(self, config_path, definition_whitelist=[]):
        super().__init__()
        conf = OPConfigParser()
        conf.read(config_path)
        defaults = conf.defaults()
        self.config_path = defaults[self.CONF_PATH_KEY]
        self.response_path = defaults[self.RESP_PATH_KEY]
        self.respdir_json_file = defaults[self.RESP_DIR_KEY]
        self.ignore_signin_fail = defaults.get(self.IGN_SIGNIN_FAIL_KEY, False)
        self.input_path = defaults.get(self.INPUT_PATH_KEY)
        response_defs = self._get_response_defs(conf, definition_whitelist)
        self.update(response_defs)

    def _get_response_defs(self, conf: OPConfigParser, whitelist: List[str]):
        response_defs = {}
        for sname in conf.sections():
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
