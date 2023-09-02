from __future__ import annotations

from typing import TYPE_CHECKING

from mock_cli import CommandInvocation

# Private imports, but we control both projects, so shouldn't be a problem
# Better than exporting API from pyonepassword that shouldn't be exposed
from ._op import OP, OPItemList, _OPArgv, op_logging

if TYPE_CHECKING:
    from ._op import OPPasswordRecipe


class OPResponseGenerationException(Exception):
    pass


class OPResponseGenerator(OP):
    logger = op_logging.console_logger("OPresponseGenerator", op_logging.DEBUG)

    @classmethod
    def _generate_response_dict(cls, argv_obj,
                                query_name,
                                stdout,
                                stderr,
                                returncode,
                                changes_state,
                                input=None):
        query_args = list(argv_obj)[1:]
        query_response = CommandInvocation(
            query_args, stdout, stderr, returncode, query_name, changes_state, input=input)

        return query_response

    def item_get_generate_response(self,
                                   item_name_or_uuid,
                                   query_name,
                                   vault=None,
                                   fields=None,
                                   include_archive=False,
                                   expected_ret=0,
                                   changes_state=False):
        item_get_argv = self._item_get_argv(
            item_name_or_uuid, vault=vault, include_archive=include_archive, fields=fields)

        resp_dict = self._generate_response(
            item_get_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def item_delete_generate_response(self,
                                      item_name_or_uuid,
                                      query_name,
                                      vault=None,
                                      archive=False,
                                      expected_ret=0,
                                      changes_state=False):
        item_delete_argv = self._item_delete_argv(
            item_name_or_uuid, archive=archive, vault=vault)

        resp_dict = self._generate_response(
            item_delete_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def item_delete_multiple_generate_response(self,
                                               vault,
                                               query_name,
                                               categories=None,
                                               include_archive=False,
                                               tags=None,
                                               archive=False,
                                               expected_ret=0,
                                               changes_state=False,
                                               title_glob=None,
                                               batch_size=25):
        if categories is None:
            categories = list()
        if tags is None:
            tags = list()
        item_list = self.item_list(categories=categories,
                                   include_archive=include_archive,
                                   tags=tags,
                                   title_glob=title_glob,
                                   vault=vault, generic_okay=True)
        start = 0
        end = len(item_list)

        item_id = "-"
        item_delete_argv = self._item_delete_argv(
            item_id, vault=vault, archive=archive)
        response_list = []

        for i in range(start, end, batch_size):
            # override "changes_state" for all except the
            # last chunk
            partial_query_name = f"{query_name}_part_{i:03d}"
            _changes_state = False
            chunk = item_list[i:i+batch_size]

            if i + batch_size >= end:
                # at the last chunk, reset _changes_state
                # to whatever was passed in
                _changes_state = changes_state
            chunk = OPItemList(chunk)
            chunk_json = chunk.serialize()
            response = self._generate_response(item_delete_argv,
                                               partial_query_name,
                                               expected_ret,
                                               changes_state=_changes_state,
                                               input=chunk_json)
            response_list.append(response)
        return response_list

    def item_edit_set_favorite_generate_response(self,
                                                 item_name_or_uuid: str,
                                                 query_name: str,
                                                 item_favorite: bool,
                                                 vault: str = None,
                                                 expected_ret: int = 0,
                                                 changes_state: bool = False) -> CommandInvocation:
        item_edit_argv = self._item_edit_set_favorite_argv(item_name_or_uuid,
                                                           item_favorite,
                                                           vault=vault)
        invocation = self._generate_response(
            item_edit_argv, query_name, expected_ret, changes_state)
        return invocation

    def item_edit_set_title_generate_response(self,
                                              item_name_or_uuid: str,
                                              query_name: str,
                                              item_title: str,
                                              vault: str = None,
                                              expected_ret: int = 0,
                                              changes_state: bool = False) -> CommandInvocation:
        item_edit_argv = self._item_edit_set_title_argv(item_name_or_uuid,
                                                        item_title,
                                                        vault=vault)
        invocation = self._generate_response(
            item_edit_argv, query_name, expected_ret, changes_state)
        return invocation

    def item_edit_set_tags_generate_response(self,
                                             item_name_or_uuid: str,
                                             query_name: str,
                                             tag_list,
                                             vault: str = None,
                                             expected_ret: int = 0,
                                             changes_state: bool = False) -> CommandInvocation:
        # tags should already be a List[str], OPConfigParser handled that for us
        item_edit_argv = self._item_edit_set_tags_argv(item_name_or_uuid,
                                                       tag_list,
                                                       vault=vault)
        invocation = self._generate_response(
            item_edit_argv, query_name, expected_ret, changes_state)
        return invocation

    def item_edit_set_password_generate_response(self,
                                                 item_name_or_uuid: str,
                                                 query_name: str,
                                                 password: str,
                                                 field_label: str,
                                                 section_label: str = None,
                                                 vault: str = None,
                                                 expected_ret: int = 0,
                                                 changes_state: bool = False) -> CommandInvocation:
        item_edit_argv = self._item_edit_set_password_argv(item_name_or_uuid,
                                                           password,
                                                           field_label,
                                                           section_label,
                                                           vault)
        invocation = self._generate_response(
            item_edit_argv, query_name, expected_ret, changes_state)
        return invocation

    def item_edit_generate_password_generate_response(self,
                                                      item_name_or_uuid: str,
                                                      query_name: str,
                                                      password_recipe: OPPasswordRecipe,
                                                      vault: str = None,
                                                      expected_ret: int = 0,
                                                      changes_state: bool = False) -> CommandInvocation:

        item_edit_argv = self._item_edit_generate_password_argv(item_name_or_uuid,
                                                                password_recipe,
                                                                vault)
        invocation = self._generate_response(
            item_edit_argv, query_name, expected_ret, changes_state)
        return invocation

    def document_get_generate_response(self,
                                       document_name_or_uuid: str,
                                       query_name,
                                       vault: str = None,
                                       include_archive: bool = False,
                                       alternate_name: str = None,
                                       expected_ret=0,
                                       changes_state=False):
        if alternate_name:
            doc_id = alternate_name
            get_doc_argv = self._document_get_argv(
                doc_id, vault=vault, include_archive=include_archive)
            normal_argv = self._document_get_argv(
                document_name_or_uuid, vault=vault)
        else:
            doc_id = document_name_or_uuid
            get_doc_argv = self._document_get_argv(
                doc_id, vault=vault, include_archive=include_archive)
            normal_argv = get_doc_argv

        resp_dict = self._generate_response(
            get_doc_argv, query_name, expected_ret, changes_state, record_argv=normal_argv)

        return resp_dict

    def document_delete_generate_response(self,
                                          document_name_or_uuid,
                                          query_name,
                                          vault=None,
                                          archive=False,
                                          expected_ret=0,
                                          changes_state=False):
        document_delete_argv = self._document_delete_argv(
            document_name_or_uuid, archive=archive, vault=vault)

        resp_dict = self._generate_response(
            document_delete_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def vault_get_generate_response(self,
                                    vault_name_or_uuid,
                                    query_name,
                                    expected_ret=0,
                                    changes_state=False):
        vault_get_argv = self._vault_get_argv(vault_name_or_uuid)

        resp_dict = self._generate_response(
            vault_get_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def vault_list_generate_response(self,
                                     query_name,
                                     group_name_or_id=None,
                                     user_name_or_id=None,
                                     expected_ret=0,
                                     changes_state=False):
        vault_list_argv = self._vault_list_argv(
            group_name_or_id=group_name_or_id, user_name_or_id=user_name_or_id)

        resp_dict = self._generate_response(
            vault_list_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def user_get_generate_response(self,
                                   user_name_or_uuid,
                                   query_name,
                                   expected_ret=0,
                                   changes_state=False):
        user_get_argv = self._user_get_argv(user_name_or_uuid)

        resp_dict = self._generate_response(
            user_get_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def user_list_generate_response(self,
                                    query_name,
                                    group_name_or_id=None,
                                    vault=None,
                                    expected_ret=0,
                                    changes_state=False):
        user_list_argv = self._user_list_argv(
            group_name_or_id=group_name_or_id, vault=vault)

        resp_dict = self._generate_response(
            user_list_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def group_get_generate_response(self,
                                    group_name_or_uuid,
                                    query_name,
                                    expected_ret=0,
                                    changes_state=False):
        group_get_argv = self._group_get_argv(group_name_or_uuid)
        resp_dict = self._generate_response(
            group_get_argv, query_name, expected_ret, changes_state)
        return resp_dict

    def group_list_generate_response(self,
                                     query_name,
                                     user_name_or_id=None,
                                     vault=None,
                                     expected_ret=0,
                                     changes_state=False):
        group_list_argv = self._group_list_argv(
            user_name_or_id=user_name_or_id, vault=vault)
        resp_dict = self._generate_response(
            group_list_argv, query_name, expected_ret, changes_state)

        return resp_dict

    @classmethod
    def cli_version(cls, query_name, expected_ret=0, changes_state=False):
        cli_version_argv = _OPArgv.cli_version_argv('op')
        resp_dict = cls._generate_response(
            cli_version_argv, query_name, expected_ret, changes_state)

        return resp_dict

    def item_list_generate_response(self,
                                    query_name,
                                    categories=None,
                                    include_archive=False,
                                    tags=None,
                                    vault=None,
                                    expected_ret=0,
                                    changes_state=False):
        if categories is None:
            categories = list()
        if tags is None:
            tags = list()

        item_list_argv = self._item_list_argv(
            categories=categories, include_archive=include_archive, tags=tags, vault=vault)

        resp_dict = self._generate_response(
            item_list_argv, query_name, expected_ret, changes_state)

        return resp_dict

    @classmethod
    def item_template_list_generate_response(cls, query_name, expected_ret=0, changes_state=False):
        template_list_argv = _OPArgv.item_template_list_argv('op')
        resp_dict = cls._generate_response(
            template_list_argv, query_name, expected_ret, changes_state)
        return resp_dict

    @classmethod
    def account_list_generate_response(cls, query_name, expected_ret=0, changes_state=False):
        account_list_argv = cls._account_list_argv()
        resp_dict = cls._generate_response(
            account_list_argv, query_name, expected_ret, changes_state)
        return resp_dict

    @classmethod
    def whoami_generate_response(cls, query_name, account=None, expected_ret=0, changes_state=False):
        whoami_argv = _OPArgv.whoami_argv('op', account=account)
        resp_dict = cls._generate_response(
            whoami_argv, query_name, expected_ret, changes_state)
        return resp_dict

    @classmethod
    def _generate_response(cls, run_argv, query_name, expected_return, changes_state, record_argv=None, input=None):
        cls.logger.info(f"About to run: {run_argv.cmd_str()}")
        if record_argv is None:
            record_argv = run_argv
        stdout, stderr, returncode = cls._run_raw(
            run_argv, capture_stdout=True, ignore_error=True, input_string=input)

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
            record_argv, query_name, stdout, stderr, returncode, changes_state, input=input)

        return resp_dict
