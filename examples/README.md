# Examples

This directory contains example usage of the generated SDK.

## Prerequisites

Before running these examples, generate the Pet Store SDK:

```bash
cd ..
uv run pydantic-openapi-sdk generate --spec example_api.yaml --out output --package petstore_sdk
```

## Examples

### Basic Usage (`basic_usage.py`)
Simple example showing:
- Client creation with authentication
- Making basic API calls
- Working with Pydantic models

```bash
python examples/basic_usage.py
```

### Complete Example (`complete_example.py`)
Comprehensive example demonstrating:
- Model validation
- Error handling
- Context manager usage
- Different API operations
- Environment variable configuration

```bash
python examples/complete_example.py
```

### Environment Variables

You can customize the examples using these environment variables:

```bash
export PETSTORE_BASE_URL="https://your-api.example.com/v1"
export PETSTORE_TOKEN="your-actual-token"
python examples/complete_example.py
```

## Notes

- These examples assume the Pet Store API from `example_api.yaml`
- The examples use mock URLs and tokens for demonstration
- Real API implementations may vary in response format
- Always handle authentication and errors appropriately in production code
