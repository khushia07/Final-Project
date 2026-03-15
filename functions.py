import base64
import urllib.parse, urllib.request, urllib.error, json
import pprint
import requests
from authlib.integrations.requests_client import OAuth2Session
from keys import client_id, client_secret, weather_api_key
from datetime import datetime


# getting the latitude and longitude of the place chosen because it is required for Open Weather
def geocode_location(location):
    baseurl = "http://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": location,
        "limit": 1,
        "appid": weather_api_key
    }

    fullurl = baseurl + "?" + urllib.parse.urlencode(params)

    try:
        resp = requests.get(fullurl)
        resp.raise_for_status()
        data = resp.json()

        if len(data) == 0:
            return None
        
        lat = data[0]["lat"]
        lon = data[0]["lon"]

        return lat, lon
    
    except Exception as e:
        print("Error in geocoding: ", e)
        return None

# figuring out how many days in advance the user wants the playlist for
# this will be needed for the free version of the weather api since it gives an 8 day forecase
def days_ahead(selected_date):
    today = datetime.now().date()
    target = datetime.strptime(selected_date, "%Y-%m-%d").date()
    return (target-today).days

# getting the weather for that date and location
def get_weather(lat, lon, selected_date):

    baseurl = "https://api.openweathermap.org/data/3.0/onecall"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": weather_api_key,
        "units": "imperial"
    }

    fullurl = baseurl + "?" + urllib.parse.urlencode(params)

    try:
        resp = requests.get(fullurl)
        resp.raise_for_status()
        data = resp.json()

        # how many days ahead, using previous function
        offset = days_ahead(selected_date)

        # use current day data if its for the same day
        if offset == 0:
            weather_data = data["current"]["weather"][0]["main"]
            return weather_data

        # otherwise use the daily forecast
        else:
            weather_data = data["daily"][offset]["weather"][0]["main"]
            return weather_data
    
    except Exception as e:
        print("Error retrieving weather: ", e)
        return None


# creating predefined logic to map each weather to a genre
def map_weather_to_genre(weather_data):
    # logic

    weather_data = weather_data.strip()
    if weather_data in ("Thunderstorm", "Drizzle", "Rain"):
        genre = "chill"
    
    elif weather_data == "Snow":
        genre = "chill"

    elif weather_data in ("Mist", "Smoke", "Haze", "Dust", "Fog", "Sand", "Ash"):
        genre = "chill"

    elif weather_data in ("Squall", "Tornado"):
        genre = "chill"

    elif weather_data == "Clear":
        genre = "chill"
    
    elif weather_data == "Clouds":
        genre = "chill"
    
    else:
        genre = "chill"

    genre = "pop"

    return genre

def get_spotify_tracks(genre, limit, token):

    # calls Spotify API
    url = "https://api.spotify.com/v1/recommendations"

    params = {
        "seed_genres": genre,
        "limit": limit
    }

    headers = {"Authorization": f"Bearer {token['access_token']}"}


    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    # if tracks exists, extract that data and start appending relevant 
    # information to a new list called tracks, and return that list
    if "tracks" in data:
        tracklist = data["tracks"]
        tracks = []
        for item in tracklist:
            tracks.append({
                "name": item["name"],
                "artist": item["artists"][0]["name"],
                "url": item["external_urls"]["spotify"]
        })   
        return tracks

    # otherwise return an empty list
    else:
        tracklist = []
        return tracklist


