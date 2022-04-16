from datetime import datetime
from tarfile import SUPPORTED_TYPES
from urllib import response
from flask import request
import requests
from package import imdb_image_prefix, imdb_title_prefix, TMDB_API_KEY, OMDB_API_KEY
import re
import json
from googlesearch import search
import imdb
from requests.utils import quote
from difflib import SequenceMatcher
from package.models import Movie

ia = imdb.IMDb()
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def getGenre():
    response = {"genres":[{"id":28,"name":"Action"},{"id":12,"name":"Adventure"},{"id":16,"name":"Animation"},{"id":35,"name":"Comedy"},{"id":80,"name":"Crime"},{"id":99,"name":"Documentary"},{"id":18,"name":"Drama"},{"id":10751,"name":"Family"},{"id":14,"name":"Fantasy"},{"id":36,"name":"History"},{"id":27,"name":"Horror"},{"id":10402,"name":"Music"},{"id":9648,"name":"Mystery"},{"id":10749,"name":"Romance"},{"id":878,"name":"Science Fiction"},{"id":10770,"name":"TV Movie"},{"id":53,"name":"Thriller"},{"id":10752,"name":"War"},{"id":37,"name":"Western"}]}
    genreList = {}
    for i in response["genres"]:
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


def findIMDBid(name):
    res = ia.search_movie(name)
    movie_id = res[0].movieID
    return "tt"+str(movie_id)


def getAddMovieDetails(url):
    imdb_id = url.split("/title/")[1][:-1]
    id, original_name, posterLink, genre, release_year, is_adult, rating, runtime, language, movie_name = "","","","","","","","","", ""
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
                # print(posterLink)
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
    # print(movie_url)
    return response

def getOMDBRes(imdb_id):
    omdb_url = "https://www.omdbapi.com/?i=" + imdb_id + "&apikey=" + OMDB_API_KEY
    response = requests.get(omdb_url).json()
    # print(omdb_url)
    return response


def fetchAllDetails(id, imdb_id):
    tmdb_details = getTMDBRes(id)
    omdb_res = getOMDBRes(imdb_id)
    return tmdb_details, omdb_res


def fetchSimilarMovies(movie):
    if movie.is_archived:
        movies = Movie.query.filter_by(is_archived=True).all()
    else:
        movies = Movie.query.filter_by(is_archived=False).all()
    
    genre = movie.genre.split(", ")
    movie_match = {}

    if "Animation" in genre:
        if "Japanese" in movie.language.split(", "):
            for i in movies:
                if movie.id != i.id and "Animation" in i.genre.split(", ") and "Japanese" in i.language:
                    temp = similar(i.name, movie.name)
                    if temp > 0.6:
                        movie_match[i] = temp
            if len(list(movie_match.keys())) < 4:
                for i in movies:
                    if movie.id != i.id and "Animation" in i.genre.split(", ") and "Japanese" in i.language:
                            movie_match[i] = similar(i.name, movie.name)
        else:
            for i in movies:
                if movie.id != i.id and "Animation" in i.genre.split(", "):
                    temp = similar(i.name, movie.name)
                    if temp > 0.6:
                        movie_match[i] = temp
            if len(list(movie_match.keys())) < 4:
                for i in movies:
                    if movie.id != i.id and "Animation" in i.genre.split(", "):
                            movie_match[i] = similar(i.name, movie.name)
    else:
        for i in movies:
            if movie.id != i.id and "Animation" not in i.genre.split(", "):
                temp = similar(i.name.split(":")[0], movie.name.split(":")[0])
                if temp > 0.6:
                    movie_match[i] = temp
        if len(list(movie_match.keys())) < 4:
            for i in movies:
                if movie.id != i.id and "Animation" not in i.genre.split(", "):
                        movie_match[i] = similar(i.name, movie.name)

    sorted_dict = dict(sorted(movie_match.items(), key=lambda item: item[1], reverse=True))
    # print(sorted_dict)
    # print([i.name for i in list(sorted_dict.keys())])
    return list(sorted_dict.keys())


def apisearch(query):
    url = 'https://api.themoviedb.org/3/search/movie?api_key='+TMDB_API_KEY+'&language=en-US&query='+quote(query)+'&page=1&include_adult=false'
    response = requests.get(url).json()
    y = response["results"]
    y.sort(key=lambda x: float(x["vote_average"]))
    d = {}
    d["results"] = y[-5:]
    d["length"] = response["total_results"]
    return d


def apisearch2(query):
    url = 'https://api.themoviedb.org/3/search/movie?api_key='+TMDB_API_KEY+'&language=en-US&query='+quote(query)+'&page=1&include_adult=true'
    response = requests.get(url).json()
    total_pages = response["total_pages"]
    y = []
    if total_pages > 1:
        for i in range(total_pages):
            url = 'https://api.themoviedb.org/3/search/movie?api_key='+TMDB_API_KEY+'&language=en-US&query='+quote(query)+'&page=' + str(i+1) +'&include_adult=true'
            response = requests.get(url).json()
            temp = response["results"]
            for movie in temp:
                y.append(movie)
    # y.sort(key=lambda x: float(x["vote_average"]))
    d = {}
    # d["results"] = y[::-1]
    d["results"] = y
    d["length"] = response["total_results"]
    return d


def fetchSavedSimilarMovies(moviegenre):
    related_movies = []
    movies = Movie.query.filter_by(is_archived=False).all()
    genre = moviegenre.split(", ")
    if "Animation" in genre:
        for i in movies:
            if "Animation" in i.genre.split(", "):
                related_movies.append(i)
    else:
        for i in movies:
            if "Animation" not in i.genre.split(", "):
                if set(genre) & set(i.genre.split(", ")):
                    related_movies.append(i)
    return related_movies


if __name__ == "__main__":
    pass