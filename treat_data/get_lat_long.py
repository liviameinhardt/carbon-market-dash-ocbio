#%%
"""
Use this script to update the latitude/longitude and GeoJSON data for the countries in WB and MVC datasets.
You may need to manually add some countries to the coordinates/feature dictionary if they are not found by the geocoder.
"""
from geopy.geocoders import Nominatim
import pandas as pd
import pickle
import requests

GEOLOCATOR = Nominatim(user_agent="geo_lookup")

def get_lat_long(locations):
    """
    Get latitude and longitude for a list of locations using Nominatim geocoder.
    
    Args:
        locations (list): List of location names (e.g., countries, cities).

    Returns:
        dict: A dictionary with location names as keys and their corresponding latitude and longitude as values.
    """

    # Load the coordinates dictionary if it exists
    with open('../data/processed/coords.pkl', 'rb') as f:
        coords = pickle.load(f)

    # Check if the coordinates for the locations are already in the dictionary
    missing_coords = [place for place in locations if place not in coords]

    if len(missing_coords):
        new_coords = {place: GEOLOCATOR.geocode(place) for place in missing_coords}

        coords.update(new_coords)

        # Lines to specific locations manually
        # coords.update({'Korea, Rep.':GEOLOCATOR.geocode('korea republic')})
        # coords.update({'Guangdong (except Shenzhen)':GEOLOCATOR.geocode('Guangdong')})

        missing_coords = [place for place in locations if place not in coords]
        print("The following locations could not be found:",missing_coords)

        with open('../data/processed/coords.pkl', 'wb') as f:
            pickle.dump(coords, f)

    return coords


def get_geo_json(place_name):
    """
    Fetch the GeoJSON boundary for a given place (country, city, or region) using OpenStreetMap's Nominatim API.
    
    Args:
        place_name (str): The name of the place (e.g., "Brazil", "Paris", "California").
        
    Returns:
        dict: The GeoJSON data for the place.
    """

    url = f"https://nominatim.openstreetmap.org/search?format=json&polygon_geojson=1&q={place_name}"
    response = requests.get(url, headers={'User-Agent': 'geojson-fetcher'})
    
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.status_code}")
    
    data = response.json()
    
    if not data:
        raise ValueError("No data found for the given place name.")
    
    return data[0]['geojson']


def get_geojson(locations,search_names=None):
    """
    Get GeoJSON data for a list of locations using OpenStreetMap's Nominatim API.
    
    Args:
        locations (list): List of location names (e.g., countries, cities).
        search_names (list): Optional list of search names to use instead of locations.
        
    Returns:
        list: A list of GeoJSON features for the locations."""

    features = []

    for cur_id, cur_location in enumerate(locations):

        # Get the GeoJSON for the current location
        try:
            cur_search = search_names[cur_id] if search_names else cur_location
            geometry = get_geo_json(cur_search)

        except Exception as e:
            print(f"Error fetching GeoJSON for {cur_location}: {e}")
            continue

        features.append({'type': 'Feature',
            'geometry': geometry,
            'properties': {"Jurisdiction covered": cur_location, "Country": cur_location},
            'id': cur_id})

    return features


def update_geojson(locations):
    """
    Update the GeoJSON data for a list of locations.
    """

    # Load the coordinates dictionary if it exists
    with open('../data/processed/geojson.pkl', 'rb') as f:
        features_list = pickle.load(f)

    missing_features = [i for i in locations if i not in [i['properties']['Country'] for i in features_list]]
    
    if len(missing_features):
        print("Searching for new features:", missing_features)
        new_features = get_geojson(missing_features)

        #use this to add specific locations
        # new_features = get_geojson(locations = ['Guangdong (except Shenzhen)', 'Korea, Rep.'],
        #                               search_names = ['Guangdong',  'Republic of Korea'])

        if len(new_features):

            features_list+=new_features

            with open('../data/processed/geojson.pkl', 'wb') as f:
                pickle.dump(features_list, f)
                
        still_missing = [i for i in missing_features if i not in [i['properties']['Country'] for i in new_features]]
        print("Still missing features:", still_missing)



def update_location_data():
    """
    Update WB and MCV datasets with latitude, longitude, and GeoJSON data.
    This function reads the datasets, fetches the required data, and updates the datasets.
    """

    def update_coords(locations):

        # Add latitude column using coords dictionary
        coords = get_lat_long(locations)

        data_wb['lat'] = data_wb['Jurisdiction covered'].map(lambda x: coords[x].latitude if coords[x] else None)
        data_wb['lon'] = data_wb['Jurisdiction covered'].map(lambda x: coords[x].longitude if coords[x] else None)

        mvc['lat'] = mvc['Country'].map(lambda x: coords[x].latitude if coords[x] else None)
        mvc['lon'] = mvc['Country'].map(lambda x: coords[x].longitude if coords[x] else None)

        data_wb.to_csv("../data/processed/wb_info.csv", sep=";", decimal=",", index=False)
        mvc.to_csv("../data/processed/mvc_credits_info.csv", sep=";", decimal=",", index=False)
        

    data_wb = pd.read_csv("../data\processed\wb_info.csv",sep=";",decimal=",")
    mvc = pd.read_csv("../data/processed/mvc_credits_info.csv",sep=";",decimal=",")
    locations = set(data_wb["Jurisdiction covered"].unique()).union(set(mvc["Country"].unique()))

    update_coords(locations)
    update_geojson(locations)

    print("Data updated successfully!")


# %%
