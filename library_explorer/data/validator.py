from rich.console import Console

from library_explorer.data.loader import DataRepository

# from library_explorer.data.models import Role, Tool
# Role and Tool not directly used yet for these specific validations

console = Console()


def validate_data(repo: DataRepository) -> bool:
    """Validates the loaded data for consistency and integrity."""
    is_valid = True
    console.print("\n[bold]Running Data Validations...[/bold]")

    # --- Tool Registry Specific Validations ---
    if (
        not repo.tool_categories_present
        and (repo.data_path / "tool_registry.json").exists()
    ):
        console.print(
            ":warning: [yellow]Validation Info:[/] 'tool_categories' key "
            "missing in 'tool_registry.json'. No tools were loaded from it."
        )
        # is_valid remains true as this might be intentional for other purposes

    if repo.tool_domain_mappings:
        console.print("  Validating tool domain mappings...")
        # Get all loaded category names from tools (derived from categories)
        loaded_category_names = set()
        if repo.tools:
            loaded_category_names = {
                tool.category for tool in repo.list_tools() if tool.category
            }

        if not loaded_category_names and repo.tool_categories_present:
            # tool_categories was present but no tools were parsed
            # The loader logic should prevent this if tool_categories has content
            console.print(
                ":warning: [yellow]Validation Info:[/] 'tool_domain_mappings' "
                "found, but no tool categories seem to be loaded to validate "
                "against."
            )
        elif not loaded_category_names and not repo.tool_categories_present:
            # This is fine, tool_categories wasn't there, so nothing to map to.
            pass  # No categories to map against, loader warned about missing
        else:
            for domain_name, mapped_categories in repo.tool_domain_mappings.items():
                for category_name in mapped_categories:
                    if category_name not in loaded_category_names:
                        console.print(
                            f":x: [bold red]Validation Error:[/] Domain "
                            f"'{domain_name}' in 'tool_domain_mappings' references "
                            f"a non-existent tool category '{category_name}'."
                        )
                        is_valid = False
            if is_valid:  # Only print if no errors found in this section
                console.print(
                    "    [green]:heavy_check_mark:[/green] Tool domain mappings "
                    "are consistent with loaded categories."
                )
    elif repo.tool_categories_present and not repo.tool_domain_mappings:
        console.print(
            ":information_source: [blue]Validation Info:[/] 'tool_categories' "
            "are present, but 'tool_domain_mappings' key is missing or empty in "
            "'tool_registry.json'."
        )

    # --- Generic Validations (placeholder until Roles/Domains loaded) ---
    # Schema validation handled by Pydantic during loading models.

    # Example: Check for orphaned tools (tools in roles but not defined)
    # Relevant when Role objects loaded with primary_tools populated.
    # if repo.roles and repo.tools:
    #     console.print("  Validating role-tool references...")
    #     all_tool_ids = set(repo.tools.keys())
    #     for role in repo.list_roles():
    #         for tool_id in role.primary_tools:
    #             if tool_id not in all_tool_ids:
    #                 console.print(
    #                     f":x: [bold red]Validation Error:[/] Role "
    #                     f"'{role.name}' references missing tool '{tool_id}'."
    #                 )
    #                 is_valid = False

    # Example: Check for missing domain references (if domains loaded)
    # Relevant when Domain objects loaded and Role/Tool have domains populated.
    # if repo.domains and (repo.roles or repo.tools):
    #     console.print("  Validating domain references...")
    #     all_domain_ids = set(repo.domains.keys())
    #     for role in repo.list_roles():
    #         for domain_id in role.domains:
    #             if domain_id not in all_domain_ids:
    #                 console.print(
    #                     f":x: [bold red]Validation Error:[/] Role "
    #                     f"'{role.name}' references missing domain '{domain_id}'."
    #                 )
    #                 is_valid = False
    #     for tool in repo.list_tools():
    #         for domain_id in tool.domains:
    #             if domain_id not in all_domain_ids:
    #                 console.print(
    #                     f":x: [bold red]Validation Error:[/] Tool "
    #                     f"'{tool.name}' references missing domain '{domain_id}'."
    #                 )
    #                 is_valid = False

    console.print("\n[bold]Validation Summary:[/bold]")
    if is_valid:
        console.print(
            ":white_check_mark: [bold green]All data validations passed "
            "successfully![/]"
        )
    else:
        console.print(
            ":x: [bold red]Data validation failed. Please review errors above.[/]"
        )

    return is_valid
