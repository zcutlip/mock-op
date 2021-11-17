from configparser import ConfigParser


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
    RESP_DIR_KEY = "response_dir_file"

    def __init__(self, config_path):
        super().__init__()
        conf = ConfigParser()
        conf.read(config_path)
        defaults = conf.defaults()
        self.config_path = defaults[self.CONF_PATH_KEY]
        self.response_path = defaults[self.RESP_PATH_KEY]
        self.respdir_json_file = defaults[self.RESP_DIR_KEY]
        response_defs = self._get_response_defs(conf)
        self.update(response_defs)

    def _get_response_defs(self, conf: ConfigParser):
        response_defs = {}
        for sname in conf.sections():
            sect = conf[sname]
            resp_def = OPresponseDefinition(sname, sect)
            response_defs[sname] = resp_def

        return response_defs
