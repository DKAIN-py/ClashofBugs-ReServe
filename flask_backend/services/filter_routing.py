import requests
from geopy.geocoders import Nominatim
import re
import numpy as np
from flask import jsonify
# data to come

"""
{
    donorlist : [{donorId,
                    address,
                    quantity,
                    food_category
                }],
    filters : {
                food_category,
                live_loc,
                closets(boolean)
                capacity
            }
}
"""



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
    location = geolocator.geocode(address, timeout=10)
    
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


def get_osrm_road_distance(origin_coords, dest_coords):
    
    lon1, lat1 = origin_coords[1], origin_coords[0]
    lon2, lat2 = dest_coords[1], dest_coords[0]
    
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

def dt_scales(dtlist:list):
    d_list, t_list = [],[]
    for dt in dtlist:
        distkm, disttime = get_osrm_road_distance(dt.get("address"))
        d_list.append(distkm)
        t_list.append(disttime)

    d_scale = np.median(np.array(d_list))
    t_scale = np.median(np.array(t_list))
    return d_scale,t_scale


def compute_scores(donorlist: list, filterlist: dict) -> list:
    """
    Computes scores for donors relative to filters.
    Uses food match + distance/time if routing is ON.
    Ignores quantity_score.
    """
    newlist = []

    # Pre-geocode all donors to get coords
    for donor in donorlist:
        if "coords" not in donor or donor["coords"] is None:
            donor["coords"] = get_coords_from_address(donor.get("address"))

    # Compute d_scale / t_scale if routing
    if filterlist.get("nearest"):
        d_list, t_list = [], []
        for donor in donorlist:
            if donor.get("coords"):
                distkm, durmin = get_osrm_road_distance(donor["coords"], filterlist.get("live_loc"))
                if distkm is not None:
                    d_list.append(distkm)
                    t_list.append(durmin)
                    donor["distance_km"] = distkm
                    donor["duration_min"] = durmin
        # Use median for scaling
        d_scale = np.median(d_list) if d_list else 1
        t_scale = np.median(t_list) if t_list else 1
    else:
        d_scale, t_scale = 1, 1  # dummy values if not using routing

    # Compute scores
    for donor in donorlist:
        # --- Food Score ---
        overlap = len(set(donor.get("food_category", [])) & set(filterlist.get("food_category", [])))
        food_score = overlap / max(1, len(filterlist.get("food_category", [])))

        # --- Distance / Time Score ---
        distance_score, time_score = 0, 0
        if filterlist.get("nearest") and donor.get("coords"):
            distance_score = 1 / (1 + donor.get("distance_km", 0) / d_scale)
            time_score = 1 / (1 + donor.get("duration_min", 0) / t_scale)

        # --- Final Score ---
        if filterlist.get("nearest"):
            final_score = 0.7 * food_score + 0.3 * time_score
        else:
            final_score = food_score

        newlist.append({
            "_id": donor["_id"],
            "food_score": round(food_score, 3),
            "distance_score": round(distance_score, 3),
            "time_score": round(time_score, 3),
            "final_score": round(final_score, 3)
        })

    
    return newlist


def filtersort(filterlsit):
    donorlist = filterlsit.get("donorli", [])
    filters = filterlsit.get("filters", {})

    reslist = compute_scores(donorlist, filters)
    # Sort descending by final_score
    reslist.sort(key=lambda x: x["final_score"], reverse=True)
    print(reslist)
    return jsonify(reslist)


# import random

# donorlist = [
#     {
#         "donorId": f"D{str(i).zfill(3)}",
#         "address": addr,
#         "food_category": random.sample(["Rice", "Bread", "Vegetables", "Fruits", "Milk", "Eggs"], k=random.randint(1,3)),
#         "quantity": random.randint(10, 100)
#     }
#     for i, addr in enumerate([
#         "Connaught Place, New Delhi, India",
#         "Karol Bagh, New Delhi, India",
#         "Rajouri Garden, New Delhi, India",
#         "Lajpat Nagar, New Delhi, India",
#         "Dwarka Sector 10, New Delhi, India",
#         "Pitampura, New Delhi, India",
#         "Janakpuri, New Delhi, India",
#         "Vasant Kunj, New Delhi, India"
#     ], start=1)
# ]

# filters = {
#     "food_category": ["Rice", "Vegetables", "Milk"],
#     "live_loc": (28.6139, 77.2090),  # Some central location in Delhi
#     "nearest": True,
#     "capacity": 50  # Optional, can be ignored
# }

# filtlist = {
#     "donorli" : donorlist,
#     "filters" : filters
# }

# from pprint import pprint

# print("=== MOCK DONORS ===")
# pprint(donorlist)
# print("\n=== FILTERS ===")
# pprint(filters)

# filtersort(filtlist)