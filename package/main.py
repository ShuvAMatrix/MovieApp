from datetime import datetime
from flask import request
import requests
from package import imdb_image_prefix, imdb_title_prefix, TMDB_API_KEY, OMDB_API_KEY
import re
import json
from googlesearch import search
import imdb

from package.models import Movie

ia = imdb.IMDb()
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}


def getGenre():
    response = requests.get("https://api.themoviedb.org/3/genre/movie/list?api_key=9f16ee7e4aa4dd9b2ce1f9c17efa52eb&language=en-US", headers=ua)
    genreList = {}
    for i in response.json()["genres"]:
        genreList[i["id"]] = i["name"]
    return genreList


def searchMovie(name):

    res = search(name, num_results=10)
    movie_id = ""
    while True:
        temp = next(res)
        if "https://www.imdb.com/title/" in temp:
            movie_id = temp.split("/title/")[1][:-1]
            break
    movie_url = "https://api.themoviedb.org/3/find/"+movie_id+"?api_key=9f16ee7e4aa4dd9b2ce1f9c17efa52eb&language=en-US&external_source=imdb_id"



def imdbSearch(name):
    res = ia.search_movie(name)
    movie_id = res[0].movieID
    url = "https://www.imdb.com/title/tt" + movie_id + "/"
    return url


def getAddMovieDetails(url):
    imdb_id = url.split("/title/")[1][:-1]
    id, original_name, posterLink, genre, release_year, is_adult, rating, runtime, language = "","","","","","","","",""
    omdb_url = "https://www.omdbapi.com/?i=" + imdb_id + "&apikey=" + OMDB_API_KEY
    res = requests.get(omdb_url, headers=ua).json()
    try:
        if res:
            movie_name = res["Title"]
            runtime = res["Runtime"]
            genre = res["Genre"]
            release_year = res["Year"]
            language = res["Language"]
            rating = res["imdbRating"]
            movie_url = "https://api.themoviedb.org/3/find/"+imdb_id+"?api_key=" +TMDB_API_KEY+"&language=en-US&external_source=imdb_id"
            movie = requests.get(movie_url).json()
            if movie["movie_results"]:
                details = movie["movie_results"][0]
                id = details["id"]
                original_name = details["original_title"]
                posterLink = imdb_image_prefix +  details["poster_path"]
                print(posterLink)
                is_adult = details["adult"]
    except:
        from package.route import genreDict
        movie_url = "https://api.themoviedb.org/3/find/"+imdb_id+"?api_key=" +TMDB_API_KEY+"&language=en-US&external_source=imdb_id"
        movie = requests.get(movie_url).json()
        if movie["movie_results"]:
            details = movie["movie_results"][0]
            id = details["id"]
            movie_name = details["title"]
            original_name = details["original_title"]
            posterLink = imdb_image_prefix +  details["poster_path"]
            is_adult = details["adult"]
            runtime = "NA"
            language = "NA"
            temp = details["genre_ids"]
            for i in temp:
                genre += genreDict[i] + ", "
            release_year = details["release_date"].split("-")[0]
            rating = details["vote_average"]
    return id, original_name, posterLink, genre, release_year, is_adult, rating, imdb_id, movie_name, runtime, language


def gsearch(q):
    query = q + " movie imdb"
    d = dict()

    try:
        res = search(query, num_results=10)
        l = []
        for i in res:
            if i.startswith("https://www.imdb.com/title/"):
                l.append(str(i))
    except:
        url = imdbSearch(" ".join(q.split(" ")[:-1]))
        l.append(url)

    d["keyword"] = q
    d["length"] = len(l)
    d["results"] = l
    d["time"] = datetime.now()
    return d


def getTMDBRes(id):
    movie_url = "https://api.themoviedb.org/3/movie/"+id+"?api_key=" +TMDB_API_KEY+"&language=en-US"
    response = requests.get(movie_url).json()
    print(movie_url)
    return response

def getOMDBRes(imdb_id):
    omdb_url = "https://www.omdbapi.com/?i=" + imdb_id + "&apikey=" + OMDB_API_KEY
    response = requests.get(omdb_url).json()
    print(omdb_url)
    return response


def fetchAllDetails(id, imdb_id):
    tmdb_details = getTMDBRes(id)
    omdb_res = getOMDBRes(imdb_id)
    return tmdb_details, omdb_res


def fetchSimilarMovies(movie):
    related_movies = []
    movies = Movie.query.filter_by(is_archived=False).all()
    genre = movie.genre.split(", ")
    if "Animation" in genre:
        for i in movies:
            if movie.id != i.id and "Animation" in i.genre.split(", "):
                related_movies.append(i)
    else:
        for i in movies:
            if movie.id != i.id and "Animation" not in i.genre.split(", "):
                if set(genre) & set(i.genre.split(", ")):
                    related_movies.append(i)
    return related_movies


if __name__ == "__main__":
    pass