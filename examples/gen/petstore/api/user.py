"""API operations for user."""

from typing import Any, Dict, List, Optional, Union
from ..client import PetStore, TypedResponse
from ..exceptions import ApiError
from ..models import *


def create_user(client: PetStore, body: User | Dict[str, Any]) -> User:
    """Create user..
    
    This can only be done by the logged in user."""
    path = f"/user"
    params = None
    response = client.request("post", path, params=params, json=body.model_dump(mode='json') if hasattr(body, 'model_dump') else body)
    return response.json()

def create_users_with_list_input(client: PetStore, body: list[User] | Dict[str, Any]) -> User:
    """Creates list of users with given input array..
    
    Creates list of users with given input array."""
    path = f"/user/createWithList"
    params = None
    response = client.request("post", path, params=params, json=body.model_dump(mode='json') if hasattr(body, 'model_dump') else body)
    return response.json()

def login_user(client: PetStore, username: Optional[str] = None, password: Optional[str] = None) -> str:
    """Logs user into the system..
    
    Log into the system."""
    path = f"/user/login"
    params = {}
    if username is not None:
        params["username"] = username
    if password is not None:
        params["password"] = password
    response = client.request("get", path, params=params)
    return response.json()

def logout_user(client: PetStore) -> TypedResponse:
    """Logs out current logged in user session..
    
    Log user out of the system."""
    path = f"/user/logout"
    params = None
    response = client.request("get", path, params=params)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

def get_user_by_name(client: PetStore, username: str) -> User:
    """Get user by user name..
    
    Get user detail based on username."""
    path = f"/user/{username}"
    params = None
    response = client.request("get", path, params=params)
    return response.json()

def update_user(client: PetStore, username: str, body: User | Dict[str, Any]) -> TypedResponse:
    """Update user resource..
    
    This can only be done by the logged in user."""
    path = f"/user/{username}"
    params = None
    response = client.request("put", path, params=params, json=body.model_dump(mode='json') if hasattr(body, 'model_dump') else body)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

def delete_user(client: PetStore, username: str) -> TypedResponse:
    """Delete user resource..
    
    This can only be done by the logged in user."""
    path = f"/user/{username}"
    params = None
    response = client.request("delete", path, params=params)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

