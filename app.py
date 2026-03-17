from flask import Flask, redirect, request, session, render_template
from authlib.integrations.requests_client import OAuth2Session
from keys import client_id, client_secret
from functions import (
    geocode_location,
    days_ahead,
    get_weather,
    map_weather_to_genre,
    get_spotify_tracks
)

app = Flask(__name__)

app.secret_key = "abcdefghijklmnopqrstuvxyz"


# this is where the user sees the form
@app.route("/", methods =["GET", "POST"])

def index():
    if request.method == "POST":
        session["date"] = request.form["date"]
        session["location"] = request.form["location"]
        session["length"] = request.form["length"]

        return redirect("/login")
    
    return render_template("index.html")

# login route
@app.route("/login")
def login():
    scope = "user-read-private user-read-email user-top-read"

    client = OAuth2Session(
        client_id,
        client_secret,
        scope=scope,
        redirect_uri="https://agrawkhu.pythonanywhere.com/callback"
    )

    authorization_endpoint = "https://accounts.spotify.com/authorize"

    uri, state = client.create_authorization_url(authorization_endpoint, show_dialog=True)

    session["oauth_state"] = state
    return redirect(uri)


# callback route
@app.route("/callback")
def callback():

    scope = "playlist-read-private"
    
    client = OAuth2Session(
        client_id,
        client_secret,
        scope = scope,
        redirect_uri="https://agrawkhu.pythonanywhere.com/callback"
    )

    token_endpoint = "https://accounts.spotify.com/api/token"

    token = client.fetch_token(
        token_endpoint,
        authorization_response=request.url
    )

    session["token"] = token
    return redirect("/results")

# generating the playlist
@app.route("/results")
def results():
    token = session.get("token")
    if token is None:
        return redirect("/login")

    # geocode coords
    coords = geocode_location(session["location"])
    if coords is None:
        return "Location not found."
    
    lat, lon = coords

    # getting weather
    weather = get_weather(lat, lon, session["date"])
    if weather is None:
        return "Weather data is unavailable."

    # mapping the result to a genre
    genre = map_weather_to_genre(weather)

    # getting tracks based on that genre
    length = int(session["length"])

    tracks = get_spotify_tracks(genre, length, token)

    return render_template("results.html",
                           genre=genre,
                           tracks=tracks,
                           weather=weather)

# running the app
if __name__ == "__main__":
    app.run(debug=True)