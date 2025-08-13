#!/usr/bin/env python3
"""Basic usage example of the generated SDK."""

import sys
from pathlib import Path

# Add the generated SDK to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "output"))

from petstore_sdk import BearerAuth, Client
from petstore_sdk.api import pets
from petstore_sdk.models import NewPet, Status


def main():
    # Create client
    client = Client(
        base_url="https://petstore.example.com/api/v1",
        auth=BearerAuth("your-token-here"),
    )

    try:
        # List pets
        pets_list = pets.list_pets(client, limit=10)
        print(f"Found {len(pets_list) if pets_list else 0} pets")

        # Create a new pet
        new_pet = NewPet(name="Buddy", tag="dog", status=Status.available)

        created_pet = pets.create_pet(client, body=new_pet.model_dump(mode="json"))
        print(f"Created pet: {created_pet}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
