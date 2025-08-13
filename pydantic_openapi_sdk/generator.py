"""Code generator for API functions and client structure."""

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from .model_generator import ModelGenerator
from .parser import OpenAPIParser
import ast


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
        self.generated_model_names: set[str] = set()

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
        self._analyze_generated_models(package_dir)
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
        param_mapping = {}  # Store original -> snake_case mapping
        
        for param in path_params:
            param_type = self._get_python_type(param["schema"])
            snake_name, original_name = self._convert_param_name(param["name"])
            param_mapping[snake_name] = original_name
            params.append(f"{snake_name}: {param_type}")
            print(f"DEBUG: Path param {operation.get('operation_id', 'unknown')}: {original_name} -> {snake_name}")

        # Query parameters
        query_params = [p for p in operation["parameters"] if p["in"] == "query"]
        for param in query_params:
            param_type = self._get_python_type(param["schema"])
            snake_name, original_name = self._convert_param_name(param["name"])
            param_mapping[snake_name] = original_name
            
            if param["required"]:
                params.append(f"{snake_name}: {param_type}")
            else:
                params.append(f"{snake_name}: Optional[{param_type}] = None")

        # Request body
        if operation["request_body"]:
            body_type = self._get_request_body_type(operation["request_body"])
            # Support both Pydantic models and raw dicts for flexibility
            if body_type != "Any" and body_type != "Dict[str, Any]":
                params.append(f"body: {body_type} | Dict[str, Any]")
            else:
                params.append(f"body: {body_type}")

        # Return type
        return_type = self._get_response_type(operation["responses"])

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
        
        # Replace path parameters with snake_case variable names
        for param in path_params:
            snake_name, original_name = self._convert_param_name(param["name"])
            final_path = final_path.replace(f"{{{original_name}}}", f"{{{snake_name}}}")

        body.append(f'    path = f"{final_path}"')

        # Build query parameters
        if query_params:
            body.append("    params = {}")
            for param in query_params:
                snake_name, original_name = self._convert_param_name(param["name"])
                if param["required"]:
                    body.append(f'    params["{original_name}"] = {snake_name}')
                else:
                    body.append(f"    if {snake_name} is not None:")
                    body.append(f'        params["{original_name}"] = {snake_name}')
        else:
            body.append("    params = None")

        # Build request call
        request_args = [f'"{method}"', "path", "params=params"]
        if operation["request_body"]:
            request_args.append("json=body.model_dump(mode='json') if hasattr(body, 'model_dump') else body")

        body.append(f"    response = client.request({', '.join(request_args)})")

        # Handle response based on return type
        if return_type == "TypedResponse":
            body.append("    return TypedResponse(")
            body.append("        status_code=response.status_code,")
            body.append("        headers=dict(response.headers),")
            body.append("        data=response.json() if response.text else None,")
            body.append("    )")
        else:
            # For typed responses, return JSON directly
            body.append("    return response.json()")

        result = signature + "\n" + docstring + "\n".join(body)
        operation_id = operation.get('operation_id', 'unknown')
        print(f"DEBUG: Generated function {operation_id}")
        print(f"DEBUG: Signature: {signature}")
        if "petId" in result or "orderId" in result:
            print(f"DEBUG: WARNING - Found camelCase in {operation_id}:")
            print(f"DEBUG: Full result:\n{result}")
        return result

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

    def _analyze_generated_models(self, package_dir: Path) -> None:
        """Analyze generated models to extract actual class and enum names."""
        models_init_path = package_dir / "models" / "__init__.py"
        if not models_init_path.exists():
            return
        
        try:
            with open(models_init_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Parse the AST to extract class and enum definitions
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                    if isinstance(node, ast.ClassDef):
                        self.generated_model_names.add(node.name)
        except Exception:
            # If parsing fails, we'll fall back to basic schema names
            pass
    
    def _resolve_model_type(self, schema: dict) -> str:
        """Resolve OpenAPI schema to Python model type."""
        if not schema:
            return "Any"
        
        # Handle $ref references
        if "$ref" in schema:
            ref_path = schema["$ref"]
            if ref_path.startswith("#/components/schemas/"):
                schema_name = ref_path.split("/")[-1]
                
                # Check if the schema name exists in generated models
                if schema_name in self.generated_model_names:
                    return schema_name
                
                # Check for common datamodel-codegen naming variations
                variations = [
                    schema_name,
                    f"{schema_name}1",  # Common suffix for conflicts
                    f"{schema_name}Model",  # Sometimes adds Model suffix
                ]
                
                for variation in variations:
                    if variation in self.generated_model_names:
                        return variation
                
                # If no match found, fall back to original name and hope for the best
                return schema_name
        
        # Handle array types
        if schema.get("type") == "array":
            items_schema = schema.get("items", {})
            item_type = self._resolve_model_type(items_schema)
            return f"list[{item_type}]"
        
        # Handle object types - could be inline schemas
        if schema.get("type") == "object":
            return "Dict[str, Any]"
        
        # Handle basic types
        schema_type = schema.get("type")
        if schema_type == "string":
            return "str"
        elif schema_type == "integer":
            return "int"
        elif schema_type == "number":
            return "float"
        elif schema_type == "boolean":
            return "bool"
        
        return "Any"

    def _get_response_type(self, responses: dict) -> str:
        """Get the appropriate return type from OpenAPI responses."""
        # Try common success status codes
        for status_code in ["200", "201", "202"]:
            if status_code in responses:
                response = responses[status_code]
                schema = response.get("schema", {})
                
                if schema:
                    return self._resolve_model_type(schema)
                
                # If no schema but response exists, use TypedResponse
                return "TypedResponse"
        
        # If no success response found, default to TypedResponse
        return "TypedResponse"
    
    def _get_request_body_type(self, request_body: dict) -> str:
        """Get the appropriate type for request body from OpenAPI request body spec."""
        schema = request_body.get("schema", {})
        
        if schema:
            return self._resolve_model_type(schema)
        
        # Default to Any for unknown schema
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
    
    def _convert_param_name(self, param_name: str) -> tuple[str, str]:
        """Convert parameter name to snake_case and return both versions.
        
        Returns:
            tuple: (snake_case_name, original_name)
        """
        snake_name = self._to_snake_case(param_name)
        return snake_name, param_name
