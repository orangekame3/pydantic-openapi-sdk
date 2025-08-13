"""API operations for pet."""

from typing import Any, Dict, List, Optional, Union
from ..client import Client, TypedResponse
from ..exceptions import ApiError
from ..models import *


def update_pet(client: Client, body: Any) -> Any:
    """Update an existing pet..
    
    Update an existing pet by Id."""
    path = f"/pet"
    params = None
    response = client.request("put", path, params=params, json=body)
    return response.json()

def add_pet(client: Client, body: Any) -> Any:
    """Add a new pet to the store..
    
    Add a new pet to the store."""
    path = f"/pet"
    params = None
    response = client.request("post", path, params=params, json=body)
    return response.json()

def find_pets_by_status(client: Client, status: str) -> Any:
    """Finds Pets by status..
    
    Multiple status values can be provided with comma separated strings."""
    path = f"/pet/findByStatus"
    params = {}
    params["status"] = status
    response = client.request("get", path, params=params)
    return response.json()

def find_pets_by_tags(client: Client, tags: List[str]) -> Any:
    """Finds Pets by tags..
    
    Multiple tags can be provided with comma separated strings. Use tag1, tag2, tag3 for testing."""
    path = f"/pet/findByTags"
    params = {}
    params["tags"] = tags
    response = client.request("get", path, params=params)
    return response.json()

def get_pet_by_id(client: Client, petId: int) -> Any:
    """Find pet by ID..
    
    Returns a single pet."""
    path = f"/pet/{petId}"
    params = None
    response = client.request("get", path, params=params)
    return response.json()

def update_pet_with_form(client: Client, petId: int, name: Optional[str] = None, status: Optional[str] = None) -> Any:
    """Updates a pet in the store with form data..
    
    Updates a pet resource based on the form data."""
    path = f"/pet/{petId}"
    params = {}
    if name is not None:
        params["name"] = name
    if status is not None:
        params["status"] = status
    response = client.request("post", path, params=params)
    return response.json()

def delete_pet(client: Client, petId: int) -> TypedResponse:
    """Deletes a pet..
    
    Delete a pet."""
    path = f"/pet/{petId}"
    params = None
    response = client.request("delete", path, params=params)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

def upload_file(client: Client, petId: int, additionalMetadata: Optional[str] = None) -> Any:
    """Uploads an image..
    
    Upload image of the pet."""
    path = f"/pet/{petId}/uploadImage"
    params = {}
    if additionalMetadata is not None:
        params["additionalMetadata"] = additionalMetadata
    response = client.request("post", path, params=params)
    return response.json()

