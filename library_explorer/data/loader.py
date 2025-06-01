import json
from pathlib import Path
from typing import TypeVar

import yaml  # No longer needs ignore
from pydantic import BaseModel, ValidationError

from library_explorer.data.models import Domain, Role, Tool

# Define a TypeVar for Pydantic models to ensure type safety
T = TypeVar("T", bound=BaseModel)


class DataRepository:
    def __init__(self, data_path: str | Path) -> None:
        self.data_path = Path(data_path)
        self.roles: dict[str, Role] = {}
        self.tools: dict[str, Tool] = {}
        self.domains: dict[str, Domain] = {}
        self.tool_domain_mappings: dict[str, list[str]] = {}
        self.tool_categories_present: bool = False

    def load_data(self) -> None:
        """Loads all data from the specified path."""
        self._load_json_file(self.data_path / "tool_registry.json", self.tools, Tool)
        # Placeholder for YAML loading
        # self._load_yaml_directory(self.data_path / "roles", self.roles, Role)
        # self._load_yaml_directory(self.data_path / "domains", self.domains, Domain)

    def _load_json_file(
        self, file_path: Path, target_dict: dict[str, T], model_class: type[T]
    ) -> None:
        if not file_path.exists():
            # TODO: Add Rich console warning
            print(f"Warning: {file_path} not found.")
            return
        with open(file_path, encoding="utf-8") as f:
            try:
                data = json.load(f)
                if model_class == Tool:
                    if "tool_categories" in data:
                        self.tool_categories_present = True
                        tool_categories = data.get("tool_categories", {})
                        for category_name, category_details in tool_categories.items():
                            category_description = category_details.get("description")
                            tool_names = category_details.get("tools", [])
                            for tool_name in tool_names:
                                try:
                                    tool_id = tool_name  # Use tool name as ID for now
                                    item_data = {
                                        "tool_id": tool_id,
                                        "name": tool_name,
                                        "category": category_name,
                                        "description": category_description,
                                        "domains": [],  # Will be populated later
                                    }
                                    # Cast item_data for model_class compatibility
                                    # This block is for Tool model_class
                                    if model_class == Tool:
                                        # item_data compatible with Tool fields
                                        item = model_class(**item_data)
                                        # T is bound by BaseModel, Tool is BaseModel
                                        # And tool_id is an attribute of Tool.
                                        target_dict[item.tool_id] = item  # type: ignore [attr-defined]
                                    else:
                                        # Fallback path for other model classes
                                        pass  # Raise error for unexpected model_class
                                except ValidationError as e:
                                    # TODO: Add Rich console error
                                    print(
                                        f"Error validating tool '{tool_name}' "
                                        f"in category '{category_name}':\\n{e}"
                                    )

                        # Load domain_mappings
                        self.tool_domain_mappings = data.get("domain_mappings", {})
                    else:
                        self.tool_categories_present = False
                        print(
                            f"Warning: 'tool_categories' key not found in "
                            f"{file_path}. No tools will be loaded from this file."
                        )
                elif isinstance(
                    data, list
                ):  # Fallback for other models or different JSON structures
                    for item_data in data:
                        try:
                            # Generic ID handling for other models
                            item_id_key = f"{model_class.__name__.lower()}_id"
                            if item_id_key not in item_data and "id" in item_data:
                                item_data[item_id_key] = item_data.pop("id")

                            item = model_class(**item_data)
                            item_id_value = getattr(item, item_id_key)
                            if not isinstance(item_id_value, str):
                                # Handle error if ID is not string for dict keys
                                print(f"Warning: Item ID {item_id_value} not string.")
                                continue
                            target_dict[item_id_value] = item
                        except ValidationError as e:
                            print(
                                f"Error validating item in {file_path}: "
                                f"{item_data.get('name', 'Unknown')}\\n{e}"
                            )
                elif (
                    isinstance(data, dict) and model_class != Tool
                ):  # Fallback for other models if they are dicts
                    for item_id, item_data in data.items():
                        try:
                            item_id_key = f"{model_class.__name__.lower()}_id"
                            if item_id_key not in item_data:
                                item_data[item_id_key] = item_id
                            item = model_class(**item_data)
                            target_dict[item_id] = item
                        except ValidationError as e:
                            print(
                                f"Error validating item {item_id} in {file_path}:\\n{e}"
                            )
                else:
                    # Fallback for unexpected Tool data structure
                    print(
                        f"Warning: Unexpected data structure in {file_path} "
                        f"for {model_class.__name__}. Expected list or dict."
                    )

            except json.JSONDecodeError as e:
                # TODO: Add Rich console error
                print(f"Error decoding JSON from {file_path}: {e}")

    def _load_yaml_directory(
        self, dir_path: Path, target_dict: dict[str, T], model_class: type[T]
    ) -> None:
        if not dir_path.is_dir():
            # TODO: Add Rich console warning
            # print(f"Warning: Directory {dir_path} not found.")
            return
        for file_path in dir_path.glob("*.yaml"):
            with open(file_path, encoding="utf-8") as f:
                try:
                    data = yaml.safe_load(f)
                    item = model_class(**data)
                    item_id_key = f"{model_class.__name__.lower()}_id"
                    item_id_value = getattr(item, item_id_key)
                    if not isinstance(item_id_value, str):
                        print(
                            f"Warning: YAML Item ID {item_id_value} for "
                            f"{file_path} is not a string, skipping."
                        )
                        continue
                    target_dict[item_id_value] = item
                except yaml.YAMLError as e:
                    # TODO: Add Rich console error
                    print(f"Error parsing YAML from {file_path}: {e}")
                except ValidationError as e:
                    # TODO: Add Rich console error
                    print(f"Error validating data from {file_path}: {e}")

    def get_role(self, role_id: str) -> Role | None:
        return self.roles.get(role_id)

    def get_tool(self, tool_id: str) -> Tool | None:
        return self.tools.get(tool_id)

    def get_domain(self, domain_id: str) -> Domain | None:
        return self.domains.get(domain_id)

    def list_roles(self) -> list[Role]:
        return list(self.roles.values())

    def list_tools(self) -> list[Tool]:
        return list(self.tools.values())

    def list_domains(self) -> list[Domain]:
        return list(self.domains.values())
