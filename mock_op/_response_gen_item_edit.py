from mock_cli import CommandInvocation

from ._op import OPPasswordRecipe
from .response_generator import OPResponseGenerator


def item_edit_set_favorite(op: OPResponseGenerator,
                           query_name,
                           query_definition,
                           item_id,
                           vault) -> CommandInvocation:

    item_favorite: bool = query_definition["item-favorite"]
    expected_return: int = query_definition.get("expected-return", 0)
    changes_state: bool = query_definition.get("changes_state", False)
    invocation = op.item_edit_set_favorite_generate_response(item_id,
                                                             query_name,
                                                             item_favorite,
                                                             vault=vault,
                                                             expected_ret=expected_return,
                                                             changes_state=changes_state)
    return invocation


def item_edit_set_title(op: OPResponseGenerator,
                        query_name,
                        query_definition,
                        item_id,
                        vault) -> CommandInvocation:

    item_title = query_definition["item-title"]
    expected_return = query_definition.get("expected-return", 0)
    changes_state = query_definition.get("changes_state", False)
    invocation = op.item_edit_set_title_generate_response(item_id,
                                                          query_name,
                                                          item_title,
                                                          vault=vault,
                                                          expected_ret=expected_return,
                                                          changes_state=changes_state)
    return invocation


def item_edit_set_password(op: OPResponseGenerator,
                           query_name,
                           query_definition,
                           item_id,
                           vault) -> CommandInvocation:

    password = query_definition["password"]
    field_label = query_definition["field_label"]
    section_label = query_definition.get("section_label", None)
    expected_return = query_definition.get("expected-return", 0)
    changes_state = query_definition.get("changes_state", False)

    invocation = op.item_edit_set_password_generate_response(item_id,
                                                             query_name,
                                                             password,
                                                             field_label,
                                                             section_label=section_label,
                                                             vault=vault,
                                                             expected_ret=expected_return,
                                                             changes_state=changes_state)
    return invocation


def item_edit_generate_password(op: OPResponseGenerator,
                                query_name,
                                query_definition,
                                item_id,
                                vault) -> CommandInvocation:

    recipe_str = query_definition["password-recipe"]
    expected_return = query_definition.get("expected-return", 0)
    changes_state = query_definition.get("changes_state", False)

    # will validate password recipe, raising OPInvalidPasswordRecipeException if
    # validation fails
    password_recipe = OPPasswordRecipe.from_string(recipe_str)

    invocation = op.item_edit_generate_password_generate_response(item_id,
                                                                  query_name,
                                                                  password_recipe,
                                                                  vault=vault,
                                                                  expected_ret=expected_return,
                                                                  changes_state=changes_state)
    return invocation


def item_edit_set_tags(op: OPResponseGenerator,
                       query_name,
                       query_definition,
                       item_id,
                       vault) -> CommandInvocation:

    tag_list = query_definition.get("tags", [])
    expected_return = query_definition.get("expected-return", 0)
    changes_state = query_definition.get("changes_state", False)
    invocation = op.item_edit_set_tags_generate_response(item_id,
                                                         query_name,
                                                         tag_list,
                                                         vault=vault,
                                                         expected_ret=expected_return,
                                                         changes_state=changes_state)
    return invocation
