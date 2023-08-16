from mock_cli import CommandInvocation

from ._op import OPInvalidPasswordRecipeException, OPPasswordRecipe
from .response_generator import OPResponseGenerator


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


def _validate_password_recipe(password_recipe: str) -> bool:
    digits = False
    symbols = False
    letters = False

    parts = password_recipe.split(",")
    passwd_len = parts.pop(0)
    for part in parts:
        if part == "letters":
            letters = True
        elif part == "digits":
            digits = True
        elif part == "symbols":
            symbols = True
        else:
            raise OPInvalidPasswordRecipeException(
                f"Invalid password recipe component: {part}")

    # if this is a valid recipe nothing happens, else an exception is raised
    recipe = OPPasswordRecipe(passwd_len, letters=letters,
                              digits=digits, symbols=symbols)

    return recipe


def item_edit_generate_password(op: OPResponseGenerator,
                                query_name,
                                query_definition,
                                item_id,
                                vault) -> CommandInvocation:
    password_recipe = query_definition["password-recipe"]
    _validate_password_recipe(password_recipe)
