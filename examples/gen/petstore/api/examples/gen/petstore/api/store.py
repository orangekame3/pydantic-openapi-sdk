"""API operations for store."""

from typing import Any, Dict, List, Optional, Union
from ..client import PetStore, TypedResponse
from ..exceptions import ApiError
from ..models import *


def get_inventory(client: PetStore) -> Dict[str, Any]:
    """Returns pet inventories by status..
    
    Returns a map of status codes to quantities."""
    path = f"/store/inventory"
    params = None
    response = client.request("get", path, params=params)
    return response.json()

def place_order(client: PetStore, body: Order | Dict[str, Any]) -> Order:
    """Place an order for a pet..
    
    Place a new order in the store."""
    path = f"/store/order"
    params = None
    response = client.request("post", path, params=params, json=body.model_dump(mode='json') if hasattr(body, 'model_dump') else body)
    return response.json()

def get_order_by_id(client: PetStore, orderId: int) -> Order:
    """Find purchase order by ID..
    
    For valid response try integer IDs with value <= 5 or > 10. Other values will generate exceptions."""
    path = f"/store/order/{orderId}"
    params = None
    response = client.request("get", path, params=params)
    return response.json()

def delete_order(client: PetStore, orderId: int) -> TypedResponse:
    """Delete purchase order by identifier..
    
    For valid response try integer IDs with value < 1000. Anything above 1000 or non-integers will generate API errors."""
    path = f"/store/order/{orderId}"
    params = None
    response = client.request("delete", path, params=params)
    return TypedResponse(
        status_code=response.status_code,
        headers=dict(response.headers),
        data=response.json() if response.text else None,
    )

