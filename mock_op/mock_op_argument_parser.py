from argparse import SUPPRESS as ARGPARSE_SUPPRESS
from argparse import ArgumentParser, _SubParsersAction


def arg_subparser_vault(subparsers: _SubParsersAction):
    # -- vault --
    parser_vault = subparsers.add_parser(
        "vault", help="Manage permissions and perform CRUD operations on your 1Password vaults")
    parser_vault_subparsers = parser_vault.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    # vault get
    parser_vault_subcmd = parser_vault_subparsers.add_parser(
        "get", description="Get details about a vault", help="Get details about a vault")
    parser_vault_subcmd.add_argument(
        "vault", metavar="{ <vaultName> | <vaultID> }", help="The user email address, name, or ID")

    # vault list
    parser_vault_subcmd = parser_vault_subparsers.add_parser(
        "list", description="List vaults.", help="List all vaults in the account")
    parser_vault_subcmd.add_argument(
        "list", help=ARGPARSE_SUPPRESS, action='store_true')
    parser_vault_subcmd.add_argument(
        "--group", metavar="string", help="List vaults a group has access to.")
    parser_vault_subcmd.add_argument(
        "--user", metavar="string", help="List vaults that a given user has access to.")


def arg_subparser_user(subparsers: _SubParsersAction):
    # -- user --
    parser_user = subparsers.add_parser(
        "user", help="Perform CRUD operations on the groups of users in your 1Password account")
    parser_user_subparsers = parser_user.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    # user get
    parser_user_subcmd = parser_user_subparsers.add_parser(
        "get", description="Get details about a user", help="Get details about a user")
    parser_user_subcmd.add_argument(
        "user", metavar="{ <email> | <name> | <userID> }", help="The user email address, name, or ID")

    # user edit
    parser_user_subcmd = parser_user_subparsers.add_parser(
        "edit", description="Change a user's name or Travel Mode status", help="Edit a user's name or Travel Mode status")
    parser_user_subcmd.add_argument(
        "user", metavar="[{ <email> | <name> | <userID> | - }] [flags]", help="The user email address, name, or ID")
    parser_user_subcmd.add_argument(
        "--name", metavar="string", help="Set the user's name.")
    parser_user_subcmd.add_argument(
        "--travel-mode", metavar="on|off", help="Turn Travel Mode on or off for the user. (default off)")

    # user list
    parser_user_subcmd = parser_user_subparsers.add_parser(
        "list", description="List users.", help="List users")
    parser_user_subcmd.add_argument(
        "list", help="List users", action='store_true')
    parser_user_subcmd.add_argument(
        "--group", help=" List users who belong to a group.")
    parser_user_subcmd.add_argument(
        "--vault", help="List users who have direct access to vault."
    )


def arg_subparser_group(subparsers: _SubParsersAction):
    # -- group --
    parser_group = subparsers.add_parser(
        "group", help="Perform CRUD operations on the groups of users in your 1Password account")
    parser_group_subparsers = parser_group.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    # group get
    parser_group_subcmd = parser_group_subparsers.add_parser(
        "get", description="Get details about a group", help="Get details about a group")
    parser_group_subcmd.add_argument(
        "group", metavar="{ <groupName> | <groupID> }", help="The group name or ID")

    # group list
    parser_group_subcmd = parser_group_subparsers.add_parser(
        "list", description="List groups.", help="List groups")
    parser_group_subcmd.add_argument(
        "list", help="List groups", action='store_true')
    parser_group_subcmd.add_argument(
        "--user", help=" List groups that a user belongs to.")
    parser_group_subcmd.add_argument(
        "--vault", help="List groups who have direct access to vault.")


def arg_subparser_document(subparsers: _SubParsersAction):
    # -- document --
    parser_document = subparsers.add_parser(
        "document", help="Perform CRUD operations on Document items in your vaults")
    parser_document_subparsers = parser_document.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    # --- document get ---
    parser_doc_subcmd = parser_document_subparsers.add_parser(
        "get", description="Download a document and print the contents.", help="Download a document")
    parser_doc_subcmd.add_argument(
        "document", metavar="<documentName>", help="The document to download")
    parser_doc_subcmd.add_argument(
        "--vault", help="Look for the document in this vault")
    parser_doc_subcmd.add_argument(
        "--include-archive", help="Include document items in the Archive.", action='store_true')

    # --- document edit ---
    parser_doc_subcmd = parser_document_subparsers.add_parser(
        "edit",
        description="""Edit a document item.
            Specify the document item to edit by its name or ID.""", help="Edit a document item")
    parser_doc_subcmd.add_argument(
        "document", metavar="<documentName>", help="The document to delete")
    parser_doc_subcmd.add_argument(
        "--file-name", metavar="name", help="Set the file's name.")
    parser_doc_subcmd.add_argument(
        "--tags", metavar="tags", help="Set the tags to the specified (comma-separated) values. An empty value will remove all tags.")
    parser_doc_subcmd.add_argument(
        "--title", metavar="title", help="Set the document item's title.")
    parser_doc_subcmd.add_argument(
        "--vault", help="Look for the document in this vault.")

    # --- document delete ---
    parser_doc_subcmd = parser_document_subparsers.add_parser(
        "delete",
        description="""Permanently delete a document.
            Use the '--archive' option to move it to the Archive instead.""", help="Delete or archive a document item")
    parser_doc_subcmd.add_argument(
        "document", metavar="<documentName>", help="The document to delete")

    parser_doc_subcmd.add_argument(
        "--archive", help="Move the document to the Archive.", action='store_true')
    parser_doc_subcmd.add_argument(
        "--vault", help="Look for the document in this vault")


def arg_subparser_item_create(parser_item_subparsers):
    # -- op item create --
    parser_item_subcmd = parser_item_subparsers.add_parser(
        "create", description="List items.", help="List items")
    parser_item_subcmd.add_argument(
        "create", action="store_true", help=ARGPARSE_SUPPRESS)

    parser_item_subcmd.add_argument(
        "--template", help="Look for the item in this vault.")


def arg_subparser_item_template(parser_item_subparsers):
    # -- op item template --
    parser_item_subcmd = parser_item_subparsers.add_parser(
        "template", description="Manage templates.", help="Get a list of templates")

    parser_item_template_subparsers = parser_item_subcmd.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    # -- op item template list --
    parser_template_subcmd = parser_item_template_subparsers.add_parser(
        "list", description="Lists available item type templates.", help="Get a list of templates")
    parser_template_subcmd.add_argument(
        "list", action="store_true", help=ARGPARSE_SUPPRESS)


def arg_subparser_item_edit(parser_item_subparsers):
    # -- op item edit --
    parser_item_subcmd = parser_item_subparsers.add_parser(
        "edit", description="Edit an item's details", help="Edit an item's details.")

    parser_item_subcmd.add_argument(
        "edit", action="store_true", help=ARGPARSE_SUPPRESS)

    parser_item_subcmd.add_argument(
        "item", metavar="{ <itemName> | <itemID> | <shareLink> }")

    parser_item_subcmd.add_argument(
        "assignment", nargs="?", metavar="<assignment>")
    parser_item_subcmd.add_argument(
        "--favorite", metavar="{ true | false }", help="Whether this item is a favorite item. Options: true, false")
    parser_item_subcmd.add_argument(
        "--generate-password", metavar="[recipe]", help="Give the item a randomly generated password.")
    parser_item_subcmd.add_argument(
        "--tags", metavar="tags",
        help="Set the tags to the specified(comma-separated) values. An empty value will remove all tags.")
    parser_item_subcmd.add_argument(
        "--title", metavar="title", help="Set the item's title.")
    parser_item_subcmd.add_argument(
        "--url", metavar="URL", help="Set the URL associated with the item")
    parser_item_subcmd.add_argument(
        "--vault", metavar="vault", help="Edit the item in this vault.")


def arg_parser_item_share(parser_item_subparsers):
    # -- op item share --
    parser_item_subcmd = parser_item_subparsers.add_parser(
        "share", description="Edit an item's details", help="Edit an item's details.")

    parser_item_subcmd.add_argument(
        "item", metavar="{ <itemName> | <itemID> }")


def arg_subparser_item(subparsers: _SubParsersAction):
    # -- item --
    parser_item = subparsers.add_parser(
        "item", help="Perform CRUD operations on the 1Password items in your vaults")

    parser_item_subparsers = parser_item.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)

    parser_item_subcmd = parser_item_subparsers.add_parser(
        "get", description="Return details about an item.", help="Get an item's details")
    parser_item_subcmd.add_argument(
        "item", metavar="<itemName>", help="The item to get")
    parser_item_subcmd.add_argument(
        "--vault", help="Look for the item in this vault.")
    parser_item_subcmd.add_argument(
        "--fields", help="Only return data from these fields. Use 'label=' to get the field by name or 'type=' to filter fields by type.", choices=["type=otp"])
    parser_item_subcmd.add_argument(
        "--include-archive", help="Include items in the Archive.", action='store_true')

    arg_subparser_item_edit(parser_item_subparsers)

    parser_item_subcmd = parser_item_subparsers.add_parser(
        "list", description="List items.", help="List items")
    parser_item_subcmd.add_argument(
        "--vault", help="Look for the item in this vault.")
    parser_item_subcmd.add_argument(
        "--include-archive", help="Include items in the Archive.", action='store_true')
    parser_item_subcmd.add_argument(
        "--categories", help="Only list items in these categories (comma-separated).")
    parser_item_subcmd.add_argument(
        "--tags", help="Only list items with these tags (comma-separated).")

    parser_item_subcmd = parser_item_subparsers.add_parser(
        "delete", description="Permanently delete an item.", help="Delete or archive an item")
    parser_item_subcmd.add_argument(
        "item", metavar="<itemName>", help="The item to get")
    parser_item_subcmd.add_argument(
        "--archive", help="Move the item to the Archive.", action='store_true')
    parser_item_subcmd.add_argument(
        "--vault", metavar="string", help="Look for the item in this vault.")

    arg_subparser_item_template(parser_item_subparsers)
    arg_subparser_item_create(parser_item_subparsers)
    arg_parser_item_share(parser_item_subparsers)


def arg_subparser_signin(subparsers: _SubParsersAction):
    # -- signin --
    parser_signin = subparsers.add_parser(
        "signin", help="Sign in to a 1Password account")
    # parser_signin.add_argument("sign_in_address", nargs="?", default=None)
    parser_signin.add_argument(
        "-r", "--raw", help="only return the session token", action='store_true')


def arg_subparser_account(subparsers: _SubParsersAction):
    # -- account --
    parser_account = subparsers.add_parser(
        "account", help="Manage your locally configured 1Password accounts")
    parser_account_subparsers = parser_account.add_subparsers(
        title="Available Commands", metavar="[command]", dest="subcommand", required=True)
    parser_acct_subcmd = parser_account_subparsers.add_parser(
        "list", help="List users and accounts set up on this device")
    parser_acct_subcmd.add_argument("list", action="store_true")


def mock_op_arg_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("--account", metavar="account",
                        help="use the account with this identifier")
    parser.add_argument(
        "--version", help="version for op", action='store_true')

    parser.add_argument(
        "--format", help="Use this output format. Can be 'human-readable' or 'json'.")

    subparsers = parser.add_subparsers(
        description="Available Commands", metavar="[command]", dest="command", required=False)

    arg_subparser_account(subparsers)
    arg_subparser_signin(subparsers)
    arg_subparser_item(subparsers)
    arg_subparser_document(subparsers)
    arg_subparser_group(subparsers)
    arg_subparser_user(subparsers)
    arg_subparser_vault(subparsers)

    # -- whoami --
    _ = subparsers.add_parser(
        "whoami", help="Get information about a signed-in account")

    return parser
