from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OMDB_API_KEY = "ecdeb546"

@app.get("/")
async def read_form(request: Request):
    message = ""
    return templates.TemplateResponse("index.html", {"request": request,"message": message})

@app.get("/movies")
async def get_movie(request: Request, title: str):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={title}"
    response = requests.get(url)
    data = response.json()
    movies = data.get("Search", [])

    movie_list = []
    for movie in movies:
        imdb_id = movie["imdbID"]
        movie_data_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
        movie_data_response = requests.get(movie_data_url)
        movie_data = movie_data_response.json()
        movie_list.append(movie_data)
    
    if not movie_list:
        message = "No results found."
    else:
        message = ""

    return templates.TemplateResponse("index.html", {"request": request, "movie_list": movie_list, "message": message})
