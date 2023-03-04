from fastapi import FastAPI, Request, Form
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import requests
import os
from bs4 import BeautifulSoup
from PIL import Image

# reading config files
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# api key here
OMDB_API_KEY = os.getenv('KEY1')
TMDB_API_KEY = os.getenv('KEY2')


@app.get("/")
async def read_form(request: Request):
    message = ""
    return templates.TemplateResponse("index.html", {"request": request, "message": message})


def image_url_filter(url):
    try:
        r = requests.get(url, stream=True)
        r.raw.decode_content = True
        img = Image.open(r.raw)
        return url
    except Exception as e:
        print(e)
        return "static/images/no_image.png"
    
# api code
@app.get("/movies")
async def get_movie(request: Request, title: str):
    # First, try to fetch the movie details from OMDB API
    omdb_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={title}"
    omdb_response = requests.get(omdb_url)
    omdb_data = omdb_response.json()

    omdb_movies = omdb_data.get("Search", [])
    movie_list = []

    # Check if OMDB API returned any movie details
    if omdb_movies:
        for movie in omdb_movies:
            imdb_id = movie["imdbID"]
            movie_data_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
            movie_data_response = requests.get(movie_data_url)
            movie_data = movie_data_response.json()
            # Create a unified format for the movie details
            unified_data = {
                "Title": movie_data.get("Title", ""),
                "Year": movie_data.get("Year", ""),
                "Plot": movie_data.get("Plot", ""),
                "imdbRating": movie_data.get("imdbRating", ""),
                "Poster": image_url_filter(movie_data.get("Poster", "")),
                "Genre": movie_data.get("Genre", ""),
                "Director": movie_data.get("Director", ""),
                "Actors": movie_data.get("Actors", "")
            }
            movie_list.append(unified_data)

    if not movie_list:
        # Search for movie by title and get the movie ID
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        search_results = search_data.get("results", [])

        if search_results:
            # Create a unified format for the movie details for each result
            for result in search_results:
                movie_id = result.get("id")
                details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
                details_response = requests.get(details_url)
                details_data = details_response.json()

                unified_data = {
                    "Title": details_data.get("title", ""),
                    "Year": details_data.get("release_date", "")[:4],
                    "Plot": details_data.get("overview", ""),
                    "imdbRating": details_data.get("vote_average", ""),
                    "Poster": image_url_filter(f"https://image.tmdb.org/t/p/w500{details_data.get('poster_path', '')}"),
                    "Genre": ", ".join([genre.get("name", "") for genre in details_data.get("genres", [])]),
                    "Director": ", ".join([crew.get("name", "") for crew in details_data.get("credits", {}).get("crew", []) if crew.get("job", "") == "Director"]),
                    "Actors": ", ".join([actor.get("name", "") for actor in details_data.get("credits", {}).get("cast", [])[:3]])
                }
                movie_list.append(unified_data)

    # If still no movie details were returned or any error occurred, 
    if not movie_list:
        message = "No results found."
        return JSONResponse({"error": "Movie not found"}, status_code=404)
    else:
        message = ""

    print(movie_list)
    return templates.TemplateResponse("search_result.html", {"request": request, "movie_list": movie_list, "message": message})


@ app.get('/random-movie-poster')
async def get_random_movie_poster():
    # Make a GET request to the website
    response=requests.get(
        'https://www.bestrandoms.com/random-movie-generator')
    # Parse the HTML content using BeautifulSoup
    soup=BeautifulSoup(response.text, 'html.parser')
    # Find the div that contains the poster image
    poster_div=soup.find('div', {'class': 'content'})

    if poster_div is not None:
        # Get the URL of the poster image
        poster_url="https://" + \
        poster_div.find('img')['src'].replace('//', '').strip()
        # Return the URL of the poster image
        return {'poster_url': poster_url}
