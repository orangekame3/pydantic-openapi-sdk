"""Code generator for API functions and client structure."""

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from .model_generator import ModelGenerator
from .parser import OpenAPIParser


class CodeGenerator:
    """Generate Python SDK code from OpenAPI specification."""

    def __init__(self, parser: OpenAPIParser, config: dict[str, Any] = None):
        self.parser = parser
        self.config = config or {}
        self.template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_sdk(self, output_dir: Path, package_name: str) -> None:
        """Generate complete SDK."""
        package_dir = output_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Generate models
        model_generator = ModelGenerator(self.parser.spec, self.config)
        model_generator.generate_models(package_dir)

        # Generate main package files
        self._generate_init_file(package_dir, package_name)
        self._generate_exceptions_file(package_dir)
        self._generate_client_file(package_dir)

        # Generate API modules
        self._generate_api_modules(package_dir)

    def _generate_init_file(self, package_dir: Path, package_name: str) -> None:
        """Generate __init__.py for the package."""
        info = self.parser.get_info()
        tags = sorted(self.parser.get_tags())
        client_class_name = self.config.get("client_class_name", "Client")

        content = f'"""Generated SDK for {info.get("title", "API")}."""\n\n'
        content += f'__version__ = "{info.get("version", "0.1.0")}"\n\n'
        content += f"from .client import {client_class_name}, BearerAuth, ApiKeyAuth, BasicAuth, TypedResponse\n"
        content += "from .exceptions import ApiError\n"

        # Import API modules
        for tag in tags:
            module_name = self._to_snake_case(tag)
            content += f"from .api import {module_name}\n"

        content += "\n__all__ = [\n"
        content += f'    "{client_class_name}",\n'
        content += '    "BearerAuth",\n'
        content += '    "ApiKeyAuth", \n'
        content += '    "BasicAuth",\n'
        content += '    "TypedResponse",\n'
        content += '    "ApiError",\n'

        for tag in tags:
            module_name = self._to_snake_case(tag)
            content += f'    "{module_name}",\n'

        content += "]\n"

        (package_dir / "__init__.py").write_text(content)

    def _generate_exceptions_file(self, package_dir: Path) -> None:
        """Generate exceptions.py."""
        template = self.template_env.get_template("exceptions.py.j2")
        content = template.render()
        (package_dir / "exceptions.py").write_text(content)

    def _generate_client_file(self, package_dir: Path) -> None:
        """Generate client.py."""
        template = self.template_env.get_template("client.py.j2")
        content = template.render(
            default_timeout=self.config.get("timeout", 30),
            user_agent=self.config.get("user_agent"),
            client_class_name=self.config.get("client_class_name", "Client"),
        )
        (package_dir / "client.py").write_text(content)

    def _generate_api_modules(self, package_dir: Path) -> None:
        """Generate API modules grouped by tags."""
        api_dir = package_dir / "api"
        api_dir.mkdir(exist_ok=True)

        # Create __init__.py for api package
        api_init_content = '"""API modules."""\n'
        (api_dir / "__init__.py").write_text(api_init_content)

        # Group operations by tag
        operations = self.parser.get_operations()
        operations_by_tag = {}

        for operation in operations:
            for tag in operation["tags"]:
                if tag not in operations_by_tag:
                    operations_by_tag[tag] = []
                operations_by_tag[tag].append(operation)

        # Generate module for each tag
        for tag, tag_operations in operations_by_tag.items():
            self._generate_tag_module(api_dir, tag, tag_operations)

    def _generate_tag_module(
        self, api_dir: Path, tag: str, operations: list[dict[str, Any]]
    ) -> None:
        """Generate API module for a specific tag."""
        module_name = self._to_snake_case(tag)
        module_file = api_dir / f"{module_name}.py"
        client_class_name = self.config.get("client_class_name", "Client")

        content = f'"""API operations for {tag}."""\n\n'
        content += "from typing import Any, Dict, List, Optional, Union\n"
        content += f"from ..client import {client_class_name}, TypedResponse\n"
        content += "from ..exceptions import ApiError\n"
        content += "from ..models import *\n\n\n"

        for operation in operations:
            content += self._generate_operation_function(operation)
            content += "\n\n"

        module_file.write_text(content)

    def _generate_operation_function(self, operation: dict[str, Any]) -> str:
        """Generate Python function for an API operation."""
        func_name = self._get_function_name(operation)
        method = operation["method"].lower()
        path = operation["path"]

        # Build function signature
        params = []
        client_class_name = self.config.get("client_class_name", "Client")
        params.append(f"client: {client_class_name}")

        # Path parameters
        path_params = [p for p in operation["parameters"] if p["in"] == "path"]
        for param in path_params:
            param_type = self._get_python_type(param["schema"])
            params.append(f"{param['name']}: {param_type}")

        # Query parameters
        query_params = [p for p in operation["parameters"] if p["in"] == "query"]
        for param in query_params:
            param_type = self._get_python_type(param["schema"])
            if param["required"]:
                params.append(f"{param['name']}: {param_type}")
            else:
                params.append(f"{param['name']}: Optional[{param_type}] = None")

        # Request body
        if operation["request_body"]:
            params.append("body: Any")  # Could be more specific with model type

        # Return type
        success_response = operation["responses"].get("200") or operation[
            "responses"
        ].get("201")
        if success_response and success_response["schema"]:
            return_type = "Any"  # Could be more specific with model type
        else:
            return_type = "TypedResponse"

        # Function signature
        signature = f"def {func_name}({', '.join(params)}) -> {return_type}:"

        # Docstring
        docstring = f'    """{operation.get("summary", "API operation")}.'
        if operation.get("description"):
            docstring += f"\n    \n    {operation['description']}"
        docstring += '"""\n'

        # Function body
        body = []

        # Build path with path parameters
        final_path = path

        body.append(f'    path = f"{final_path}"')

        # Build query parameters
        if query_params:
            body.append("    params = {}")
            for param in query_params:
                if param["required"]:
                    body.append(f'    params["{param["name"]}"] = {param["name"]}')
                else:
                    body.append(f"    if {param['name']} is not None:")
                    body.append(f'        params["{param["name"]}"] = {param["name"]}')
        else:
            body.append("    params = None")

        # Build request call
        request_args = [f'"{method}"', "path", "params=params"]
        if operation["request_body"]:
            request_args.append("json=body")

        body.append(f"    response = client.request({', '.join(request_args)})")

        # Handle response
        if success_response and success_response["schema"]:
            body.append("    return response.json()")  # Could parse to model
        else:
            body.append("    return TypedResponse(")
            body.append("        status_code=response.status_code,")
            body.append("        headers=dict(response.headers),")
            body.append("        data=response.json() if response.text else None,")
            body.append("    )")

        return signature + "\n" + docstring + "\n".join(body)

    def _get_function_name(self, operation: dict[str, Any]) -> str:
        """Generate function name from operation."""
        if operation["operation_id"]:
            return self._to_snake_case(operation["operation_id"])

        # Generate from method and path
        method = operation["method"].lower()
        path = operation["path"]

        # Simple heuristic: method + last path segment
        path_parts = [p for p in path.split("/") if p and not p.startswith("{")]
        name = f"{method}_{path_parts[-1]}" if path_parts else method

        return self._to_snake_case(name)

    def _get_python_type(self, schema: dict[str, Any]) -> str:
        """Convert JSON schema type to Python type."""
        schema_type = schema.get("type", "any")

        if schema_type == "string":
            return "str"
        elif schema_type == "integer":
            return "int"
        elif schema_type == "number":
            return "float"
        elif schema_type == "boolean":
            return "bool"
        elif schema_type == "array":
            item_type = self._get_python_type(schema.get("items", {}))
            return f"List[{item_type}]"
        elif schema_type == "object":
            return "Dict[str, Any]"
        else:
            return "Any"

    def _to_snake_case(self, name: str) -> str:
        """Convert string to snake_case."""
        # Replace non-alphanumeric with underscore
        name = re.sub(r"[^a-zA-Z0-9]", "_", name)
        # Insert underscore before uppercase letters
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
        # Convert to lowercase and remove duplicate underscores
        name = re.sub("_+", "_", name.lower())
        # Remove leading/trailing underscores
        return name.strip("_")
