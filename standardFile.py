import google.generativeai as genai
import requests
import folium
import json
import random
from IPython.display import display
import ipywidgets as widgets

GEMINI_API_KEY = "AIzaSyD77rABCHvvE_mz5DySTZn0l0zDlIb__h0"   # e.g. "AI...something"
MAPBOX_API_KEY = "pk.eyJ1IjoidmFydW5tMDQiLCJhIjoiY21oYXZwcHZvMHFjcTJpcG04M3NvNDh2ZCJ9.HqPWUREu_pGcw12dtduWyw"

genai.configure(api_key=GEMINI_API_KEY)

def parse_user_query(query):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    Extract structured search filters from this home search query:
    "{query}"
    Return JSON with keys: bedrooms, max_price, location.
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        return {"raw_text": response.text}

def get_coordinates(location):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json"
    params = {"access_token": MAPBOX_API_KEY, "limit": 1}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    return data["features"][0]["center"][::-1]  # lat, lon

def mock_home_listings(center, count=5):
    lat, lon = center
    homes = []
    for i in range(count):
        homes.append({
            "price": random.randint(1200, 3500),
            "bedrooms": random.choice([1,2,3]),
            "latitude": lat + random.uniform(-0.02,0.02),
            "longitude": lon + random.uniform(-0.02,0.02),
            "address": f"{random.randint(100,999)} Example St"
        })
    return homes

def show_map(home):
    m = folium.Map(
        location=[home["latitude"], home["longitude"]],
        zoom_start=15,
        tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{{z}}/{{x}}/{{y}}?access_token={MAPBOX_API_KEY}",
        attr="Mapbox"
    )
    popup_text = f"{home['bedrooms']} BR, ${home['price']}<br>{home['address']}"
    folium.Marker([home["latitude"], home["longitude"]], popup=popup_text).add_to(m)
    display(m)

# --- Example usage ---
query = input("Enter your search query: ")
filters = parse_user_query(query)
location_for_coords = filters.get("location") or query
center_coords = get_coordinates(location_for_coords)
homes = mock_home_listings(center_coords, count=5)

addresses = [home["address"] for home in homes]
dropdown = widgets.Dropdown(options=addresses, description='Select:')
display(dropdown)

def on_select(change):
    selected_address = change['new']
    selected_home = next(h for h in homes if h["address"]==selected_address)
    show_map(selected_home)

dropdown.observe(on_select, names='value')
