#!/usr/bin/env python3
"""Test script using the real Swagger Pet Store API."""

import sys
from pathlib import Path

# Add the generated SDK to the path
sys.path.insert(0, str(Path(__file__).parent / "gen"))

from petstore_sdk import ApiError, Client
from petstore_sdk.api import pet, store, user
from petstore_sdk.models import Category, Pet, Tag


def test_real_api():
    """Test with the real Swagger Pet Store API."""
    # The real API base URL
    client = Client(base_url="https://petstore3.swagger.io/api/v3")

    try:
        print("🐕 Testing Real Swagger Pet Store API")
        print("=" * 50)

        # Test 1: Find pets by status
        print("\n1. Finding pets by status 'available'...")
        try:
            available_pets = pet.find_pets_by_status(client, status="available")
            print(
                f"✅ Found {len(available_pets) if available_pets else 0} available pets"
            )

            if available_pets and len(available_pets) > 0:
                first_pet = available_pets[0]
                print(
                    f"   First pet: {first_pet.get('name', 'Unknown')} (ID: {first_pet.get('id', 'N/A')})"
                )
        except ApiError as e:
            print(f"❌ Error finding pets: {e.status_code} - {e.message}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # Test 2: Get store inventory
        print("\n2. Getting store inventory...")
        try:
            inventory = store.get_inventory(client)
            print(f"✅ Store inventory retrieved: {inventory}")
        except ApiError as e:
            print(f"❌ Error getting inventory: {e.status_code} - {e.message}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # Test 3: Try to get a specific pet (might fail if ID doesn't exist)
        print("\n3. Trying to get pet with ID 1...")
        try:
            specific_pet = pet.get_pet_by_id(client, petId=1)
            print(f"✅ Pet found: {specific_pet.get('name', 'Unknown')}")
        except ApiError as e:
            if e.status_code == 404:
                print("ℹ️  Pet with ID 1 not found (expected)")
            else:
                print(f"❌ API error: {e.status_code} - {e.message}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

        # Test 4: Test model creation (no API call)
        print("\n4. Testing model creation...")
        try:
            test_pet = Pet(
                id=12345,
                name="Test Doggie",
                category=Category(id=1, name="Dogs"),
                photoUrls=["https://example.com/photo1.jpg"],
                tags=[Tag(id=1, name="friendly")],
                status="available",
            )
            print(f"✅ Pet model created: {test_pet.name}")
            print(f"   Pet data: {test_pet.model_dump(mode='json')}")
        except Exception as e:
            print(f"❌ Model creation error: {e}")

        print("\n🎉 Real API test completed!")
        print("\n💡 Notes:")
        print("- The real Pet Store API is publicly accessible")
        print("- Some operations may require authentication")
        print("- Data is shared among all users")
        print("- Generated SDK works with real OpenAPI specification!")

    finally:
        client.close()


def demo_all_endpoints():
    """Show all available endpoints in the generated SDK."""
    print("\n📚 Available API Endpoints:")
    print("=" * 50)

    print("\n🐾 Pet endpoints:")
    pet_endpoints = [
        attr
        for attr in dir(pet)
        if not attr.startswith("_") and callable(getattr(pet, attr))
    ]
    for endpoint in pet_endpoints:
        func = getattr(pet, endpoint)
        print(
            f"   - {endpoint}: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}"
        )

    print("\n🏪 Store endpoints:")
    store_endpoints = [
        attr
        for attr in dir(store)
        if not attr.startswith("_") and callable(getattr(store, attr))
    ]
    for endpoint in store_endpoints:
        func = getattr(store, endpoint)
        print(
            f"   - {endpoint}: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}"
        )

    print("\n👤 User endpoints:")
    user_endpoints = [
        attr
        for attr in dir(user)
        if not attr.startswith("_") and callable(getattr(user, attr))
    ]
    for endpoint in user_endpoints:
        func = getattr(user, endpoint)
        print(
            f"   - {endpoint}: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}"
        )


if __name__ == "__main__":
    test_real_api()
    demo_all_endpoints()
