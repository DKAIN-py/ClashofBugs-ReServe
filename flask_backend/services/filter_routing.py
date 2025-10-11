import requests
from geopy.geocoders import Nominatim
import re
import numpy as np
from flask import jsonify

def get_coords_from_address(address):
    """
    Convert a text address to (lat, lon) using OSM Nominatim.
    """
    if not address or not address.strip():
        return None
    
    address = address.strip()
    address = re.sub(r"[^A-Za-z0-9,\.\-\/ ]+", "", address)
    
    abbreviations = {
        r"\bSt\b": "Street",
        r"\bRd\b": "Road",
        r"\bAve\b": "Avenue",
        r"\bBlvd\b": "Boulevard",
        r"\bLn\b": "Lane",
        r"\bDr\b": "Drive",
        r"\bHwy\b": "Highway",
        r"\bSq\b": "Square",
        r"\bPl\b": "Place"
    }
    for abbr, full in abbreviations.items():
        address = re.sub(abbr, full, address, flags=re.IGNORECASE)
    
    address = re.sub(r"\s+", " ", address)
    
    geolocator = Nominatim(user_agent="food_donation_app")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        print(f"Geocoding failed for '{address}': {e}")
        return None


def get_osrm_road_distance(origin_coords, dest_coords):
    """
    origin_coords: (lat, lon)
    dest_coords: (lat, lon)
    Returns: (distance_km, duration_min)
    """
    if not origin_coords or not dest_coords:
        return None, None
    
    lat1, lon1 = origin_coords
    lat2, lon2 = dest_coords
    
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    
    try:
        res = requests.get(url, timeout=5).json()
        if "routes" in res and len(res["routes"]) > 0:
            distance_km = res["routes"][0]["distance"] / 1000
            duration_min = res["routes"][0]["duration"] / 60
            return distance_km, duration_min
        else:
            return None, None
    except Exception as e:
        print(f"OSRM request failed: {e}")
        return None, None


def compute_scores(donorlist: list, filterlist: dict) -> list:
    """
    Computes scores for donors relative to filters.
    Uses food match + distance/time if routing is ON.
    """
    newlist = []
    
    # Get receiver location from filters
    receiver_location = filterlist.get("location")  # [lat, lon]
    if receiver_location:
        receiver_coords = tuple(receiver_location)  # Convert to (lat, lon)
    else:
        receiver_coords = None

    # Pre-geocode all donors to get coords
    for donor in donorlist:
        if "coords" not in donor or donor["coords"] is None:
            coords = get_coords_from_address(donor.get("address"))
            donor["coords"] = coords

    # Compute d_scale / t_scale if routing
    if filterlist.get("nearest") and receiver_coords:
        d_list, t_list = [], []
        for donor in donorlist:
            if donor.get("coords"):
                distkm, durmin = get_osrm_road_distance(donor["coords"], receiver_coords)
                if distkm is not None:
                    d_list.append(distkm)
                    t_list.append(durmin)
                    donor["distance_km"] = distkm
                    donor["duration_min"] = durmin
        # Use median for scaling
        d_scale = np.median(d_list) if d_list else 1
        t_scale = np.median(t_list) if t_list else 1
    else:
        d_scale, t_scale = 1, 1

    # Get selected food category from filters
    selected_category = filterlist.get("food_category", "all")
    filter_categories = [selected_category] if selected_category != "all" else []

    # Compute scores
    for donor in donorlist:
        # --- Food Score ---
        if selected_category == "all":
            food_score = 1.0  # Match everything
        else:
            # Check if donor's food_category matches the selected one
            donor_categories = donor.get("food_category", [])
            if selected_category in donor_categories:
                food_score = 1.0
            else:
                food_score = 0.0

        # --- Distance / Time Score ---
        distance_score, time_score = 0, 0
        if filterlist.get("nearest") and donor.get("coords") and receiver_coords:
            distance_score = 1 / (1 + donor.get("distance_km", 0) / d_scale)
            time_score = 1 / (1 + donor.get("duration_min", 0) / t_scale)

        # --- Final Score ---
        if filterlist.get("nearest"):
            final_score = 0.7 * food_score + 0.3 * time_score
        else:
            final_score = food_score

        newlist.append({
            "_id": donor.get("_id"),  # Use donation_id instead of _id
            "food_score": food_score,
            "distance_score": distance_score,
            "time_score": time_score,
            "final_score": final_score,
            "distance_km": donor.get("distance_km"),
            "duration_min": donor.get("duration_min")
        })

    return newlist


def filtersort(data: dict) -> list:
    """
    Main function to filter and sort donations.
    Expected input:
    {
        "donorlist": [...],
        "filters": {...}
    }
    """
    donorlist = data.get("donorlist", [])
    filters = data.get("filters", {})

    if not donorlist:
        print("Warning: donorlist is empty")
        return []

    reslist = compute_scores(donorlist, filters)
    
    # Sort descending by final_score
    reslist.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Apply capacity limit if specified
    capacity = filters.get("capacity", 10)
    reslist = reslist[:capacity]
    
    print(f"Filtered {len(reslist)} donations out of {len(donorlist)}")
    
    return reslist