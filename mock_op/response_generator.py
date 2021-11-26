from mock_cli import CommandInvocation

# Private imports, but we control both projects, so shouldn't be a problem
# Better than exporting API from pyonepassword that shouldn't be exposed
from ._op import OP


class OPResponseGenerator(OP):

    def _generate_response_dict(self, argv_obj,
                                query_name,
                                stdout,
                                stderr,
                                returncode):
        query_args = argv_obj.query_args()
        query_response = CommandInvocation(
            query_args, stdout, stderr, returncode, query_name)

        return query_response

    def get_item_generate_response(self, item_name_or_uuid, query_name, vault=None, fields=None):
        get_item_argv = self._get_item_argv(
            item_name_or_uuid, vault=vault, fields=fields)
        self.logger.info(f"About to run: {get_item_argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            get_item_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(
            get_item_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def get_document_generate_response(self, document_name_or_uuid: str, query_name, vault: str = None,
                                       alternate_name: str = None):
        if alternate_name:
            doc_id = alternate_name
            get_doc_argv = self._get_document_argv(doc_id, vault=vault)
            normal_argv = self._get_document_argv(
                document_name_or_uuid, vault=vault)
        else:
            doc_id = document_name_or_uuid
            get_doc_argv = self._get_document_argv(doc_id, vault=vault)
            normal_argv = get_doc_argv

        self.logger.info(f"About to run: {get_doc_argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            get_doc_argv, capture_stdout=True, ignore_error=True)

        resp_dict = self._generate_response_dict(
            normal_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def get_vault_generate_response(self, vault_name_or_uuid, query_name):
        get_vault_argv = self._get_vault_argv(vault_name_or_uuid)
        self.logger.info(f"About to run: {get_vault_argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            get_vault_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(
            get_vault_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def get_user_generate_response(self, user_name_or_uuid, query_name):
        get_user_argv = self._get_user_argv(user_name_or_uuid)
        self.logger.info(f"About to run: {get_user_argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            get_user_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(
            get_user_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def get_group_generate_response(self, group_name_or_uuid, query_name):
        get_group_argv = self._get_group_argv(group_name_or_uuid)
        resp_dict = self._resp_dict_from_argv(get_group_argv, query_name)
        return resp_dict

    def cli_version(self, query_name):
        cli_version_argv = self._cli_version_argv()
        self.logger.info(f"About to run: {cli_version_argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            cli_version_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(
            cli_version_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def _resp_dict_from_argv(self, argv, query_name):
        self.logger.info(f"About to run: {argv.cmd_str()}")
        stdout, stderr, returncode = self._run_raw(
            argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(
            argv, query_name, stdout, stderr, returncode)

        return resp_dict
