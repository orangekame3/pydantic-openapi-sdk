"""OpenAPI specification parser."""

import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import yaml


class OpenAPIParser:
    """Parser for OpenAPI 3.x specifications."""

    def __init__(self, spec_input: Path | str):
        self.spec_input = spec_input
        self.spec: dict[str, Any] = {}
        self._load_spec()

    def _load_spec(self) -> None:
        """Load OpenAPI specification from file or URL."""
        if isinstance(self.spec_input, str) and self.spec_input.startswith(
            ("http://", "https://")
        ):
            # Load from URL
            try:
                with urlopen(self.spec_input) as response:
                    content = response.read().decode("utf-8")
                    # Assume JSON for URLs, but try YAML if JSON fails
                    try:
                        self.spec = json.loads(content)
                    except json.JSONDecodeError:
                        self.spec = yaml.safe_load(content)
            except Exception as e:
                raise ValueError(
                    f"Failed to load OpenAPI specification from URL {self.spec_input}: {e}"
                )
        else:
            # Load from file
            spec_path = Path(self.spec_input)
            if not spec_path.exists():
                raise FileNotFoundError(
                    f"OpenAPI specification file not found: {spec_path}"
                )

            with open(spec_path, encoding="utf-8") as f:
                if spec_path.suffix.lower() in [".yaml", ".yml"]:
                    self.spec = yaml.safe_load(f)
                elif spec_path.suffix.lower() == ".json":
                    self.spec = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {spec_path.suffix}")

    def get_info(self) -> dict[str, Any]:
        """Get API info section."""
        return self.spec.get("info", {})

    def get_servers(self) -> list[dict[str, Any]]:
        """Get servers configuration."""
        return self.spec.get("servers", [])

    def get_base_url(self) -> str | None:
        """Get base URL from servers."""
        servers = self.get_servers()
        if servers:
            return servers[0].get("url")
        return None

    def get_tags(self) -> set[str]:
        """Get all tags from operations."""
        tags = set()
        paths = self.spec.get("paths", {})

        for path_data in paths.values():
            for method_data in path_data.values():
                if isinstance(method_data, dict):
                    operation_tags = method_data.get("tags", [])
                    tags.update(operation_tags)

        if not tags:
            tags.add("default")

        return tags

    def get_operations(self) -> list[dict[str, Any]]:
        """Get all operations with metadata."""
        operations = []
        paths = self.spec.get("paths", {})

        for path, path_data in paths.items():
            for method, operation_data in path_data.items():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                ]:
                    continue

                if not isinstance(operation_data, dict):
                    continue

                operation = {
                    "path": path,
                    "method": method.upper(),
                    "operation_id": operation_data.get("operationId"),
                    "summary": operation_data.get("summary", ""),
                    "description": operation_data.get("description", ""),
                    "tags": operation_data.get("tags", ["default"]),
                    "parameters": self._parse_parameters(
                        operation_data.get("parameters", [])
                    ),
                    "request_body": self._parse_request_body(
                        operation_data.get("requestBody")
                    ),
                    "responses": self._parse_responses(
                        operation_data.get("responses", {})
                    ),
                    "security": operation_data.get("security", []),
                }
                operations.append(operation)

        return operations

    def _parse_parameters(
        self, parameters: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Parse operation parameters."""
        parsed = []
        for param in parameters:
            parsed_param = {
                "name": param.get("name"),
                "in": param.get("in"),
                "required": param.get("required", False),
                "description": param.get("description", ""),
                "schema": param.get("schema", {}),
            }
            parsed.append(parsed_param)
        return parsed

    def _parse_request_body(
        self, request_body: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Parse request body specification."""
        if not request_body:
            return None

        content = request_body.get("content", {})
        json_content = content.get("application/json")

        if json_content:
            return {
                "required": request_body.get("required", False),
                "description": request_body.get("description", ""),
                "schema": json_content.get("schema", {}),
            }

        return None

    def _parse_responses(self, responses: dict[str, Any]) -> dict[str, Any]:
        """Parse response specifications."""
        parsed = {}
        for status_code, response_data in responses.items():
            content = response_data.get("content", {})
            json_content = content.get("application/json")

            parsed[status_code] = {
                "description": response_data.get("description", ""),
                "schema": json_content.get("schema", {}) if json_content else {},
            }

        return parsed

    def get_components_schemas(self) -> dict[str, Any]:
        """Get component schemas for model generation."""
        return self.spec.get("components", {}).get("schemas", {})

    def get_security_schemes(self) -> dict[str, Any]:
        """Get security schemes."""
        return self.spec.get("components", {}).get("securitySchemes", {})
