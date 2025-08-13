# Pydantic OpenAPI SDK Generator

> [!WARNING]
> **⚠️ Under Development**  
> This project is currently under development and experimental. APIs, interfaces, and generated code structure may change in future versions. Use with caution in production environments.

Generate Python SDKs from OpenAPI 3.x specifications with Pydantic v2 models and synchronous HTTP clients.

## Features

- **OpenAPI 3.x Support** - Parse YAML/JSON specifications and URLs
- **Synchronous HTTP Client** - Built on httpx for production use
- **Pydantic v2 Models** - Generated using datamodel-code-generator for accuracy
- **Multiple Authentication** - Bearer token, API key, and Basic auth
- **YAML Configuration** - Manage generation settings in config files
- **Code Organization** - Operations grouped by tags, clean structure
- **Type Safety** - Full type hints throughout generated code
- **Error Handling** - Structured exception management
- **Make Integration** - Unified build and test workflows

## Installation

```bash
pip install pydantic-openapi-sdk
```

Or with uv:

```bash
uv add pydantic-openapi-sdk
```

## Quick Start

### 1. Generate SDK

From command line:

```bash
pydantic-openapi-sdk generate --spec openapi.yaml --out ./sdk --package my_api
```

From URL:

```bash
pydantic-openapi-sdk generate --spec https://api.example.com/openapi.json --out ./sdk --package my_api
```

With configuration file:

```bash
pydantic-openapi-sdk generate --config config.yaml
```

### 2. Use Generated SDK

```python
from my_api import Client, BearerAuth
from my_api.api import users
from my_api.models import User

client = Client(
    base_url="https://api.example.com",
    auth=BearerAuth("your-token")
)

# Make API calls
user_list = users.get_users(client, limit=10)
new_user = users.create_user(client, body={"name": "John", "email": "john@example.com"})
```

## Configuration

### YAML Configuration File

Create a configuration file to manage settings:

```yaml
# config.yaml
spec: "https://api.example.com/openapi.json"
output_dir: "./sdk"
package_name: "my_api"
base_url: "https://api.example.com"
verbose: true

# Code generation options
use_union_operator: true

# Model generation options (passed to datamodel-code-generator)
model_options:
  field_constraints: true              # Generate field constraints
  use_standard_typing: false          # Use typing_extensions
  use_generic_container_types: true   # Use list[T] instead of List[T]

# Client options
timeout: 30
user_agent: "MyApp/1.0.0"
client_class_name: "ApiClient"  # Custom client class name (default: "Client")
```

### CLI Options

| Option          | Description             | Example                      |
| --------------- | ----------------------- | ---------------------------- |
| `--config`      | Configuration file path | `--config config.yaml`       |
| `--spec`        | OpenAPI spec file/URL   | `--spec openapi.json`        |
| `--out`         | Output directory        | `--out ./generated`          |
| `--package`     | Package name            | `--package my_sdk`           |
| `--base-url`    | Default base URL        | `--base-url https://api.com` |
| `--timeout`     | HTTP timeout (seconds)  | `--timeout 60`               |
| `--client-name` | Client class name       | `--client-name ApiClient`    |
| `--verbose`     | Verbose output          | `--verbose`                  |

CLI options override configuration file settings.

## Generated SDK Structure

```text
my_api/
├── __init__.py          # Package exports
├── client.py            # HTTP client and authentication
├── exceptions.py        # Error classes
├── api/
│   ├── __init__.py
│   ├── users.py         # User operations
│   └── orders.py        # Order operations
└── models/
    └── __init__.py      # Pydantic models
```

## Usage Examples

### Basic Client Usage

```python
from my_api import Client, ApiError
from my_api.api import users

client = Client(base_url="https://api.example.com")

try:
    users_data = users.get_users(client)
    print(f"Found {len(users_data)} users")
except ApiError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

### Authentication

```python
from my_api import Client, BearerAuth, ApiKeyAuth, BasicAuth

# Bearer token
client = Client(
    base_url="https://api.example.com",
    auth=BearerAuth("your-jwt-token")
)

# API key
client = Client(
    base_url="https://api.example.com",
    auth=ApiKeyAuth("your-api-key", "X-API-Key")
)

# Basic auth
client = Client(
    base_url="https://api.example.com",
    auth=BasicAuth("username", "password")
)
```

### Working with Models

```python
from my_api.models import User, CreateUser
from pydantic import ValidationError

# Create model with validation
try:
    user_data = CreateUser(
        name="John Doe",
        email="john@example.com",
        age=30
    )
    # Convert to dict for API call
    api_payload = user_data.model_dump()
except ValidationError as e:
    print(f"Validation error: {e}")

# Parse response data
response_data = {"id": 1, "name": "John Doe", "email": "john@example.com"}
user = User(**response_data)
```

### Error Handling

```python
from my_api import ApiError
from my_api.api import users

try:
    user = users.get_user(client, user_id=123)
except ApiError as e:
    if e.status_code == 404:
        print("User not found")
    elif e.status_code == 401:
        print("Authentication required")
    elif e.status_code >= 500:
        print("Server error")
    print(f"Full error: {e.body}")
```

### Context Manager

```python
from my_api import Client, BearerAuth

with Client(base_url="https://api.example.com", auth=BearerAuth("token")) as client:
    data = users.get_users(client)
    # Client automatically closes
```

## Development

### Setup

```bash
git clone https://github.com/orangekame3/pydantic-openapi-sdk
cd pydantic-openapi-sdk
make dev
```

### Available Commands

```bash
make help                 # Show available commands
make install             # Install dependencies
make dev                 # Set up development environment
make generate-sdk        # Generate SDK from config
make test               # Test generated SDK
make test-local         # Generate and test locally
make test-real-api      # Full test with real API
make lint               # Run code linting
make format             # Format code
make clean              # Clean generated files
```

### Testing with Real APIs

Test the generator with the Swagger Pet Store API:

```bash
# Full test cycle
make test-real-api

# Or step by step
make download-spec
make generate-local-spec
make test
```

This downloads the official Pet Store OpenAPI spec, generates an SDK, and runs tests against the live API.

## Real-World Example

The repository includes a complete example using the Swagger Pet Store API:

```python
from petstore_sdk import Client
from petstore_sdk.api import pet

client = Client(base_url="https://petstore3.swagger.io/api/v3")
available_pets = pet.find_pets_by_status(client, status="available")
print(f"Found {len(available_pets)} available pets")
```

See [`examples/`](examples/) for complete working examples.

## Architecture

This generator uses:

- **[datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator)** - Generates accurate Pydantic v2 models from OpenAPI schemas
- **Jinja2 templates** - Generates client code and API operations
- **httpx** - HTTP client for generated SDKs
- **Custom OpenAPI parser** - Handles operations, parameters, and routing

## Requirements

- Python ≥ 3.10
- Dependencies: httpx, pydantic[email], pyyaml, click, jinja2, datamodel-code-generator

## Current Limitations

- Synchronous client only (async support planned)
- Basic response type mapping
- Manual pagination handling
- Limited file upload support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make check` to verify code quality
5. Submit a pull request

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.
