import logging
from mock_cli import CommandInvocation


# Private imports, but we control both projects, so shouldn't be a problem
# Better than exporting API from pyonepassword that shouldn't be exposed
from ._op import OP, _OPArgv


class OPResponseGenerationException(Exception):
    pass


class OPResponseGenerator(OP):
    logging.basicConfig(format="%(message)s", level=logging.DEBUG)
    logger = logging.getLogger()

    @classmethod
    def _generate_response_dict(cls, argv_obj,
                                query_name,
                                stdout,
                                stderr,
                                returncode):
        query_args = list(argv_obj)[1:]
        query_response = CommandInvocation(
            query_args, stdout, stderr, returncode, query_name)

        return query_response

    def item_get_generate_response(self, item_name_or_uuid, query_name, vault=None, fields=None, expected_ret=0):
        item_get_argv = self._item_get_argv(
            item_name_or_uuid, vault=vault, fields=fields)

        resp_dict = self._generate_response(
            item_get_argv, query_name, expected_ret)

        return resp_dict

    def document_get_generate_response(self,
                                       document_name_or_uuid: str,
                                       query_name,
                                       vault: str = None,
                                       alternate_name: str = None,
                                       expected_ret=0):
        if alternate_name:
            doc_id = alternate_name
            get_doc_argv = self._get_document_argv(doc_id, vault=vault)
            normal_argv = self._get_document_argv(
                document_name_or_uuid, vault=vault)
        else:
            doc_id = document_name_or_uuid
            get_doc_argv = self._get_document_argv(doc_id, vault=vault)
            normal_argv = get_doc_argv

        resp_dict = self._generate_response(
            get_doc_argv, query_name, expected_ret, record_argv=normal_argv)

        return resp_dict

    def vault_get_generate_response(self, vault_name_or_uuid, query_name, expected_ret=0):
        vault_get_argv = self._vault_get_argv(vault_name_or_uuid)

        resp_dict = self._generate_response(
            vault_get_argv, query_name, expected_ret)

        return resp_dict

    def vault_list_generate_response(self, query_name, group_name_or_id=None, user_name_or_id=None, expected_ret=0):
        vault_list_argv = self._vault_list_argv(
            group_name_or_id=group_name_or_id, user_name_or_id=user_name_or_id)

        resp_dict = self._generate_response(
            vault_list_argv, query_name, expected_ret)

        return resp_dict

    def user_get_generate_response(self, user_name_or_uuid, query_name, expected_ret=0):
        user_get_argv = self._user_get_argv(user_name_or_uuid)

        resp_dict = self._generate_response(
            user_get_argv, query_name, expected_ret)

        return resp_dict

    def user_list_generate_response(self, query_name, group_name_or_id=None, vault=None, expected_ret=0):
        user_list_argv = self._user_list_argv(
            group_name_or_id=group_name_or_id, vault=vault)

        resp_dict = self._generate_response(
            user_list_argv, query_name, expected_ret)

        return resp_dict

    def group_get_generate_response(self, group_name_or_uuid, query_name, expected_ret=0):
        group_get_argv = self._group_get_argv(group_name_or_uuid)
        resp_dict = self._generate_response(
            group_get_argv, query_name, expected_ret)
        return resp_dict

    def group_list_generate_response(self, query_name, user_name_or_id=None, vault=None, expected_ret=0):
        group_list_argv = self._group_list_argv(
            user_name_or_id=user_name_or_id, vault=vault)
        resp_dict = self._generate_response(
            group_list_argv, query_name, expected_ret)

        return resp_dict

    @classmethod
    def cli_version(cls, query_name, expected_ret=0):
        cli_version_argv = _OPArgv.cli_version_argv('op')
        resp_dict = cls._generate_response(
            cli_version_argv, query_name, expected_ret)

        return resp_dict

    def item_list_generate_response(self,
                                    query_name,
                                    categories=[],
                                    include_archive=False,
                                    tags=[],
                                    vault=None,
                                    expected_ret=0):
        item_list_argv = self._item_list_argv(
            categories=categories, include_archive=include_archive, tags=tags, vault=vault)

        resp_dict = self._generate_response(
            item_list_argv, query_name, expected_ret)

        return resp_dict

    @classmethod
    def item_template_list_generate_response(cls, query_name, expected_ret=0):
        template_list_argv = _OPArgv.item_template_list_argv('op')
        resp_dict = cls._generate_response(
            template_list_argv, query_name, expected_ret)
        return resp_dict

    @classmethod
    def account_list_generate_response(cls, query_name, expected_ret=0):
        account_list_argv = cls._account_list_argv()
        resp_dict = cls._generate_response(
            account_list_argv, query_name, expected_ret)
        return resp_dict

    @classmethod
    def whoami_generate_response(cls, query_name, account=None, expected_ret=0):
        print(account)
        whoami_argv = _OPArgv.whoami_argv('op', account=account)
        print(whoami_argv)
        resp_dict = cls._generate_response(
            whoami_argv, query_name, expected_ret)
        return resp_dict

    @classmethod
    def _generate_response(cls, run_argv, query_name, expected_return, record_argv=None):
        cls.logger.info(f"About to run: {run_argv.cmd_str()}")
        if record_argv is None:
            record_argv = run_argv
        stdout, stderr, returncode = cls._run_raw(
            run_argv, capture_stdout=True, ignore_error=True)

        if returncode != expected_return:
            cls.logger.error(
                f"Unexpected return code: expected {expected_return}, got {returncode}")
            if returncode == 0:
                cls.logger.warn(f"stdout: {stdout.decode('utf-8')}")
            else:
                cls.logger.warn(f"stderr: {stderr.decode('utf-8')}")
            raise OPResponseGenerationException(
                f"Unexpected return code: expected {expected_return}, got {returncode}")

        resp_dict = cls._generate_response_dict(
            record_argv, query_name, stdout, stderr, returncode)

        return resp_dict
