from cProfile import run
from urllib import response
from flask import Flask, request, redirect, flash
from flask import render_template
import random
import os
import csv
from package.main import getAddMovieDetails, gsearch, getGenre, fetchAllDetails, fetchSimilarMovies
from flask_login import login_user, current_user, logout_user, login_required
from package import app, db
from package.models import Movie, User
from package.cutomClasses import CustomThread
import threading
import time

#initialize list
genreDict = getGenre()


@app.route("/login", methods={"GET", "POST"})
def login():
    if current_user.is_authenticated:
        print(current_user)
        return redirect("/home")
    if request.method == "POST":
        email =  request.form["mail"]
        password = request.form["pass"]
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            if "remember" in list(request.form.keys()):
                login_user(user, request.form["remember"])
            else:
                login_user(user)
            next_page = request.args.get('next')
            print(next_page)
            flash("Welcome Back", "success")
            return redirect(next_page) if next_page else redirect("/all")
        else:
            flash(f"Invalid email or password!", "danger")
    return render_template("login.html")


@app.route("/", methods={"GET", "POST"})
@login_required
def view():
    # movies = Movie.query.filter_by(is_archived=False).all()
    # return render_template("index.html", movies=movies, user=current_user)
    tile_per_row = 4
    results = Movie.query.filter_by(is_archived=False).all()
    moviesLists = []
    for i in range(0, len(results), tile_per_row):
        moviesLists.append(results[i:i+tile_per_row]) 
    return render_template("view.html", moviesLists=moviesLists, user=current_user)


@app.route("/googlesearch/<query>", methods={"GET", "POST"})
def searchJSON(query):
    response = gsearch(query)
    return response


@app.route("/add", methods={"GET", "POST"})
@login_required
def add():
    if request.method == "POST":
        movie_name_given = request.form["moviename"]
        movie_URL = request.form["movieURL"]
        imdb_URL = request.form["imdbURL"]
        id, original_name, posterLink, genre, release_year, is_adult, rating, imdb_id, movie_name, runtime, language = getAddMovieDetails(imdb_URL)
        movie = Movie(id=id, imdb_id=imdb_id, name=movie_name, original_name=original_name, release_year=release_year, posterLink=posterLink,
                    directLink=movie_URL,genre=genre, imdb_rating=rating, is_adult=is_adult, runtime=runtime, language=language)
        db.session.add(movie)
        db.session.commit()
        flash(f"Movie has been saved!", "success")
        return redirect("/")


@app.route("/all", methods={"GET", "POST"})
@login_required
def all():
    tile_per_row = 4
    results = Movie.query.filter_by(is_archived=False).all()
    moviesLists = []
    for i in range(0, len(results), tile_per_row):
        moviesLists.append(results[i:i+tile_per_row]) 
    return render_template("view.html", moviesLists=moviesLists, user=current_user)


@app.route("/category/<cat>", methods={"GET", "POST"})
@login_required
def category(cat):
    tile_per_row = 4
    allMovies = Movie.query.filter_by(is_archived=False).all()
    temp = []
    movieLists = []
    if cat == "Science Fiction":
        for i in allMovies:
            if cat in i.genre.split(", ") or "Sci-Fi" in i.genre.split(", "):
                temp.append(i)
    else:
        for i in allMovies:
            if cat in i.genre.split(", "):
                temp.append(i)
    for j in range(0, len(temp), tile_per_row):
        movieLists.append(temp[j:j+tile_per_row])

    temp = cat
    return render_template("view.html", moviesLists=movieLists, user=current_user, cat=cat)


@app.route("/archive/<id>", methods={"GET", "POST"})
@login_required
def archive(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        movie.is_archived = True
        db.session.add(movie)
        db.session.commit()
        flash(f"Movie has been archived!", "success")
        return redirect("/")


@app.route("/bin", methods={"GET", "POST"})
@login_required
def bin():
    if request.method == "GET":
        tile_per_row = 4
        results = Movie.query.filter_by(is_archived=True).all()
        moviesLists = []
        for i in range(0, len(results), tile_per_row):
            moviesLists.append(results[i:i+tile_per_row]) 
        return render_template("view.html", moviesLists=moviesLists, user=current_user)


@app.route("/delete/<id>", methods={"GET", "POST"})
@login_required
def delete(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        db.session.delete(movie)
        db.session.commit()
        flash(f"Movie has been archived!", "success")
        return redirect("/bin")


@app.route("/restore/<id>", methods={"GET", "POST"})
@login_required
def restore(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        movie.is_archived = False
        db.session.add(movie)
        db.session.commit()
        flash(f"Movie has been restored!", "success")
        return redirect("/")



@app.route("/details/<id>", methods={"GET", "POST"})
@login_required
def details(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        tmdb_info = {}
        omdb_info = {}
        related_movies = []

        #For testing
        from package.cutomClasses import tmdb_info, omdb_info

        #Without threading
        tmdb_info, omdb_info = fetchAllDetails(id, movie.imdb_id)
        related_movies = fetchSimilarMovies(movie)
        
        #With Threading
        # t1 = CustomThread(target=fetchAllDetails, args=(id, movie.imdb_id, ))
        # t2 = CustomThread(target=fetchSimilarMovies, args=(movie,))
        # t1.start()
        # t2.start()
        # tmdb_info, omdb_info = t1.join()
        # related_movies = t2.join()
        print(related_movies)
        return render_template("details.html", user=current_user, movie=movie, tmdb_info=tmdb_info, omdb_info=omdb_info, related_movies=related_movies)