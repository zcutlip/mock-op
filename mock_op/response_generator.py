from mock_cli.responses import CommandInvocation

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
        query_response = CommandInvocation(query_args, stdout, stderr, returncode, query_name)

        return query_response

    def get_item_generate_response(self, item_name_or_uuid, query_name, vault=None, fields=None):
        get_item_argv = self._get_item_argv(item_name_or_uuid, vault=vault, fields=fields)
        stdout, stderr, returncode = self._run_raw(get_item_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(get_item_argv, query_name, stdout, stderr, returncode)

        return resp_dict

    def get_document_generate_response(self, document_name_or_uuid: str, query_name, vault: str = None):
        get_doc_argv = self._get_document_argv(
            document_name_or_uuid, vault=vault)
        stdout, stderr, returncode = self._run_raw(
            get_doc_argv, capture_stdout=True, ignore_error=True)
        resp_dict = self._generate_response_dict(get_doc_argv, query_name, stdout, stderr, returncode)

        return resp_dict
