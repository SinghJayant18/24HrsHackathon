"""
Geocoding utilities for address parsing and delivery calculations.
"""
from datetime import datetime, timedelta
import re


# Shop location: Jaipur, Rajasthan
SHOP_LAT = 26.9124
SHOP_LNG = 75.7873
SHOP_CITY = "Jaipur"
SHOP_STATE = "Rajasthan"


def parse_address_for_coords(address: str | None) -> tuple[float | None, float | None]:
    """
    Simple address parsing to extract approximate coordinates.
    For production, use a proper geocoding API (Google Maps, OpenStreetMap).
    """
    if not address:
        return None, None

    # Try to extract common patterns
    # This is a simplified version; in production use a geocoding API
    address_lower = address.lower()

    # Common city coordinates (approximate)
    city_coords = {
        "jaipur": (26.9124, 75.7873),
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bangalore": (12.9716, 77.5946),
        "kolkata": (22.5726, 88.3639),
        "chennai": (13.0827, 80.2707),
        "hyderabad": (17.3850, 78.4867),
        "pune": (18.5204, 73.8567),
        "ahmedabad": (23.0225, 72.5714),
        "surat": (21.1702, 72.8311),
    }

    for city, (lat, lng) in city_coords.items():
        if city in address_lower:
            return lat, lng

    # Default: return Jaipur coordinates if no match
    return SHOP_LAT, SHOP_LNG


def calculate_expected_delivery(
    order_date: datetime, address: str | None
) -> tuple[datetime, str]:
    """
    Calculate expected delivery date (max 5 days from order date).
    Returns (delivery_datetime, formatted_string).
    """
    base_days = 2  # Minimum 2 days
    max_days = 5

    # Simple logic: if address contains certain keywords, add days
    if address:
        address_lower = address.lower()
        if any(
            keyword in address_lower
            for keyword in ["remote", "rural", "village", "taluka"]
        ):
            delivery_days = max_days
        elif any(keyword in address_lower for keyword in ["metro", "city"]):
            delivery_days = base_days + 1
        else:
            delivery_days = base_days + 2
    else:
        delivery_days = base_days + 2

    delivery_days = min(delivery_days, max_days)
    delivery_date = order_date + timedelta(days=delivery_days)

    # Format: "DD MMM YYYY, HH:MM AM/PM"
    formatted = delivery_date.strftime("%d %b %Y, %I:%M %p")

    return delivery_date, formatted

