"""Configuration management for pydantic-openapi-sdk."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class GenerationConfig(BaseModel):
    """Configuration for SDK generation."""

    spec: str = Field(..., description="Path or URL to OpenAPI specification")
    output_dir: str = Field(".", description="Output directory for generated SDK")
    package_name: str = Field(..., description="Name of the generated package")
    base_url: str | None = Field(
        None, description="Default base URL for the API client"
    )
    verbose: bool = Field(False, description="Enable verbose output")

    # Code generation options
    use_union_operator: bool = Field(
        True, description="Use | syntax for union types (Python 3.10+)"
    )

    # Model generation options
    model_options: dict[str, Any] = Field(
        default_factory=lambda: {
            "field_constraints": True,
            "use_standard_typing": False,
            "use_generic_container_types": True,
        },
        description="Options passed to datamodel-code-generator",
    )

    # Client options
    timeout: int = Field(30, description="Default HTTP timeout in seconds")
    user_agent: str | None = Field(None, description="Custom User-Agent header")
    client_class_name: str = Field("Client", description="Name for the generated client class")


def load_config(config_path: Path) -> GenerationConfig:
    """Load configuration from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()

    if suffix == ".yaml" or suffix == ".yml":
        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config file format: {suffix}. Use .yaml or .yml")

    return GenerationConfig(**config_data)


def merge_config_with_args(
    config: GenerationConfig, **cli_args: Any
) -> GenerationConfig:
    """Merge configuration with command line arguments. CLI args take precedence."""
    config_dict = config.model_dump()

    # Only override with CLI args that are explicitly provided (not None)
    for key, value in cli_args.items():
        if value is not None:
            config_dict[key] = value

    return GenerationConfig(**config_dict)
