#!/usr/bin/env python3
"""Complete example usage of the generated Pet Store SDK.

This example demonstrates:
- Creating and configuring a client
- Authentication setup
- Making various API calls
- Error handling
- Working with Pydantic models
"""

import os
import sys
from pathlib import Path

# Add the generated SDK to the path for this example
sys.path.insert(0, str(Path(__file__).parent.parent / "output"))

from petstore import ApiError, BearerAuth, PetStore
from petstore.api import pets
from petstore.models import NewPet, Status
from pydantic import ValidationError


def create_client():
    """Create and configure the API client."""
    # You can use environment variables for configuration
    base_url = os.getenv("PETSTORE_BASE_URL", "https://petstore.example.com/api/v1")
    token = os.getenv("PETSTORE_TOKEN", "demo-token")

    return PetStore(base_url=base_url, auth=BearerAuth(token), timeout=30.0)


def demonstrate_model_validation():
    """Show Pydantic model validation in action."""
    print("=== Model Validation Demo ===")

    try:
        # Valid pet
        valid_pet = NewPet(name="Buddy", tag="dog", status=Status.available)
        print(f"✅ Valid pet created: {valid_pet.model_dump()}")

        # Invalid pet - this will raise ValidationError
        try:
            invalid_pet = NewPet(name="")  # Empty name should fail validation
            print(f"❌ This shouldn't print: {invalid_pet}")
        except ValidationError as e:
            print(f"✅ Validation caught empty name: {e}")

    except Exception as e:
        print(f"❌ Unexpected error in validation demo: {e}")


def demonstrate_api_calls(client):
    """Demonstrate various API operations."""
    print("\n=== API Operations Demo ===")

    try:
        # Create a new pet
        new_pet_data = NewPet(name="Rex", tag="dog", status=Status.available)

        print("Creating new pet...")
        created_pet = pets.create_pet(client, body=new_pet_data.model_dump(mode="json"))
        pet_id = created_pet.get("id")

        if pet_id:
            print(f"✅ Created pet with ID: {pet_id}")

            # Retrieve the pet
            print(f"Retrieving pet {pet_id}...")
            retrieved_pet = pets.get_pet(client, petId=pet_id)
            print(f"✅ Retrieved pet: {retrieved_pet.get('name', 'Unknown')}")

            # List all pets with limit
            print("Listing pets...")
            all_pets = pets.list_pets(client, limit=5)
            print(f"✅ Found {len(all_pets) if all_pets else 0} pets")

            # Clean up - delete the pet
            print(f"Deleting pet {pet_id}...")
            delete_result = pets.delete_pet(client, petId=pet_id)
            print("✅ Pet deleted successfully")

        else:
            print("❌ Failed to get pet ID from creation response")

    except ApiError as e:
        print(f"❌ API error {e.status_code}: {e.message}")

        # Handle specific error codes
        if e.status_code == 401:
            print("💡 Tip: Check your authentication token")
        elif e.status_code == 404:
            print("💡 Tip: The requested resource was not found")
        elif e.status_code >= 500:
            print("💡 Tip: Server error - try again later")

        print(f"Response body: {e.body}")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def demonstrate_error_handling(client):
    """Show comprehensive error handling."""
    print("\n=== Error Handling Demo ===")

    try:
        # Try to get a pet that doesn't exist
        print("Trying to get non-existent pet...")
        pets.get_pet(client, petId=999999)
        print("❌ This shouldn't print - pet should not exist")

    except ApiError as e:
        print(f"✅ Caught API error as expected: HTTP {e.status_code}")

    except Exception as e:
        print(f"❌ Unexpected error type: {e}")


def demonstrate_context_manager():
    """Show using client as context manager."""
    print("\n=== Context Manager Demo ===")

    try:
        base_url = os.getenv("PETSTORE_BASE_URL", "https://petstore.example.com/api/v1")
        token = os.getenv("PETSTORE_TOKEN", "demo-token")

        # Using context manager ensures client is properly closed
        with PetStore(base_url=base_url, auth=BearerAuth(token)) as client:
            print("✅ Client created with context manager")

            # Make a simple API call
            pets_list = pets.list_pets(client, limit=3)
            print(f"✅ Retrieved {len(pets_list) if pets_list else 0} pets")

        print("✅ Client automatically closed")

    except Exception as e:
        print(f"❌ Error in context manager demo: {e}")


def main():
    """Run all demonstrations."""
    print("🐕 Pet Store SDK Demo")
    print("=" * 50)

    # Show model validation
    demonstrate_model_validation()

    # Create client
    print("\n=== Client Setup ===")
    client = create_client()
    print(f"✅ Client created for: {client.base_url}")

    try:
        # Demonstrate API calls
        demonstrate_api_calls(client)

        # Show error handling
        demonstrate_error_handling(client)

    except Exception as e:
        print(f"❌ Fatal error: {e}")

    finally:
        # Always close the client
        client.close()
        print("\n✅ Client connection closed")

    # Show context manager usage
    demonstrate_context_manager()

    print("\n🎉 Demo completed!")
    print("\n💡 Tips:")
    print("- Set PETSTORE_BASE_URL environment variable for custom API URL")
    print("- Set PETSTORE_TOKEN environment variable for authentication")
    print("- Check the generated SDK code in output/petstore_sdk/")


if __name__ == "__main__":
    main()
