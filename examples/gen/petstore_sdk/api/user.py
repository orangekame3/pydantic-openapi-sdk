"""API operations for user."""

from typing import Any, Dict, List, Optional, Union
from ..client import Client, TypedResponse
from ..exceptions import ApiError
from ..models import *


def create_user(client: Client, body: Any) -> Any:
    """Create user..
    
    This can only be done by the logged in user."""
    path = f"/user"
    params = None
    response = client.request("post", path, params=params, json=body)
    return response.json()

def create_users_with_list_input(client: Client, body: Any) -> Any:
    """Creates list of users with given input array..
    
    Creates list of users with given input array."""
    path = f"/user/createWithList"
    params = None
    response = client.request("post", path, params=params, json=body)
    return response.json()

def login_user(client: Client, username: Optional[str] = None, password: Optional[str] = None) -> Any:
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

def logout_user(client: Client) -> TypedResponse:
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

def get_user_by_name(client: Client, username: str) -> Any:
    """Get user by user name..
    
    Get user detail based on username."""
    path = f"/user/{username}"
    params = None
    response = client.request("get", path, params=params)
    return response.json()

def update_user(client: Client, username: str, body: Any) -> TypedResponse:
    """Update user resource..
    
    This can only be done by the logged in user."""
    path = f"/user/{username}"
    params = None
    response = client.request("put", path, params=params, json=body)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

def delete_user(client: Client, username: str) -> TypedResponse:
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

