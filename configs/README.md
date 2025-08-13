# Configuration Files

This directory contains example configuration files for pydantic-openapi-sdk.

## Usage

### Using YAML configuration
```bash
uv run pydantic-openapi-sdk generate --config configs/petstore.yaml
```

### Override with CLI arguments
```bash
# Use config file but override package name
uv run pydantic-openapi-sdk generate --config configs/petstore.yaml --package my_custom_sdk

# Override output directory
uv run pydantic-openapi-sdk generate -c configs/petstore.yaml --out ./my_output
```

## Configuration Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `spec` | string | **required** | Path or URL to OpenAPI specification |
| `output_dir` | string | `"."` | Output directory for generated SDK |
| `package_name` | string | **required** | Name of the generated package |
| `base_url` | string | `null` | Default base URL for the API client |
| `verbose` | boolean | `false` | Enable verbose output |
| `use_union_operator` | boolean | `true` | Use `\|` syntax for union types (Python 3.10+) |
| `model_options` | object | see below | Options passed to datamodel-code-generator |
| `timeout` | integer | `30` | Default HTTP timeout in seconds |
| `user_agent` | string | `null` | Custom User-Agent header |

### Model Options

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `field_constraints` | boolean | `true` | Generate field constraints |
| `use_standard_typing` | boolean | `false` | Use standard typing instead of typing_extensions |
| `use_generic_container_types` | boolean | `true` | Use generic container types |

## File Format

YAML format is supported:

- **YAML**: `.yaml` or `.yml` extension

## Examples

See the example configuration file:
- [`petstore.yaml`](./petstore.yaml) - YAML format example
