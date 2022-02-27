from ast import keyword
from cProfile import run
from multiprocessing.sharedctypes import Value
from turtle import pos
from unittest import result
from urllib import response
from flask import Flask, request, redirect, flash
from flask import render_template
import json
from package.main import findIMDBid, getAddMovieDetails, gsearch, getGenre, fetchAllDetails, fetchSimilarMovies, apisearch, getOMDBRes, getTMDBRes, fetchSavedSimilarMovies
from flask_login import login_user, current_user, logout_user, login_required
from package import app, db, imdb_image_prefix, imdb_title_prefix
from package.models import Movie, SavedMovies, User, SavedQueries, MovieRequest
from package.cutomClasses import CustomThread
import threading
import time

#initialize list
genreDict = getGenre()


@app.route("/login", methods={"GET", "POST"})
def login():
    if current_user.is_authenticated:
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
            flash("Welcome Back", "success")
            return redirect(next_page) if next_page else redirect("/all")
        else:
            flash(f"Invalid email or password!", "danger")
    return render_template("login.html")


@app.route("/", methods={"GET", "POST"})
@login_required
def view():
    movies = Movie.query.filter_by(is_archived=False).all()
    popularMovies = Movie.query.filter_by(is_archived=False).order_by(Movie.imdb_rating.desc()).all()[:4]
    newMovies = Movie.query.filter_by(is_archived=False).order_by(Movie.release_year.desc()).all()[:4]
    animeMovies = Movie.query.filter_by(is_archived=False).filter(Movie.genre.contains("Animation")).all()[:4]
    return render_template("index.html", popularMovies=popularMovies, newMovies=newMovies, animeMovies=animeMovies, user=current_user)
    # tile_per_row = 4
    # results = Movie.query.filter_by(is_archived=False).all()
    # moviesLists = []
    # for i in range(0, len(results), tile_per_row):
    #     moviesLists.append(results[i:i+tile_per_row]) 
    # return render_template("view.html", moviesLists=moviesLists, user=current_user)


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
    return render_template("view.html", moviesLists=moviesLists, user=current_user, all="active")


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
    return render_template("view.html", moviesLists=movieLists, user=current_user, cat=cat, active=cat, category="active")


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
        return render_template("view.html", moviesLists=moviesLists, user=current_user, bin="active")


@app.route("/delete/<id>", methods={"GET", "POST"})
@login_required
def delete(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        db.session.delete(movie)
        db.session.commit()
        flash(f"Movie has been archived!", "success")
        return redirect("/bin")



@app.route("/new", methods={"GET", "POST"})
@login_required
def new():
    tile_per_row = 4
    moviesLists = []
    if request.method == "GET":
        results = Movie.query.filter_by(is_archived=False).order_by(Movie.release_year.desc()).all()
        for i in range(0, len(results), tile_per_row):
            moviesLists.append(results[i:i+tile_per_row]) 
        return render_template("view.html", moviesLists=moviesLists, user=current_user, new="active")



@app.route("/popular", methods={"GET", "POST"})
@login_required
def popular():
    tile_per_row = 4
    moviesLists = []
    if request.method == "GET":
        results1 = Movie.query.filter_by(is_archived=False).filter(Movie.imdb_rating != "N/A").order_by(Movie.imdb_rating.desc()).all()
        results = results1 + Movie.query.filter_by(is_archived=False).filter_by(imdb_rating="N/A").all()
        for i in range(0, len(results), tile_per_row):
            moviesLists.append(results[i:i+tile_per_row]) 
        return render_template("view.html", moviesLists=moviesLists, user=current_user, popular="active")



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
    movie = Movie.query.filter_by(id=id).first()
    tmdb_info = {}
    omdb_info = {}
    related_movies = []
    if request.method == "GET":
        saved_movie = SavedMovies.query.filter_by(id=id).first()
        if not saved_movie:
            tmdb_info, omdb_info = fetchAllDetails(id, movie.imdb_id)
            save_movie = SavedMovies(id=id, imdb_id=movie.imdb_id, keywords=movie.name, tmdb_data=json.dumps(tmdb_info), omdb_data=json.dumps(omdb_info))
            db.session.add(save_movie)
            db.session.commit()
        else:
            tmdb_info = json.loads(saved_movie.tmdb_data)
            omdb_info = json.loads(saved_movie.omdb_data)

        #For testing
        # from package.cutomClasses import tmdb_info, omdb_info

        #Without threading
        related_movies = fetchSimilarMovies(movie)
        #With Threading
        # t1 = CustomThread(target=fetchAllDetails, args=(id, movie.imdb_id, ))
        # t2 = CustomThread(target=fetchSimilarMovies, args=(movie,))
        # t1.start()
        # t2.start()
        # tmdb_info, omdb_info = t1.join()
        # related_movies = t2.join()
        return render_template("details.html", user=current_user, movie=movie, tmdb_info=tmdb_info, omdb_info=omdb_info, related_movies=related_movies, value="hidden")


@app.route("/language/<lang>", methods={"GET", "POST"})
@login_required
def language(lang):
    tile_per_row = 4
    moviesLists = []
    langMovies = []
    d = {"bengali":"active", "english":"active"}
    if request.method == "GET":
        results = Movie.query.filter_by(is_archived=False).order_by(Movie.name.asc()).all()
        for i in results:
            if lang.casefold() in i.language.casefold():
                langMovies.append(i)
        for i in range(0, len(langMovies), tile_per_row):
            moviesLists.append(langMovies[i:i+tile_per_row]) 
        return render_template("view.html", moviesLists=moviesLists, user=current_user, active=lang, language="active")


@app.route("/apisearch/<query>", methods={"GET", "POST"})
@login_required
def apisearchq(query):
    savedQuery = SavedQueries.query.filter_by(keyword=query.casefold()).first()
    if savedQuery:
        print("from save")
        return json.loads(savedQuery.data)
    else:
        result = apisearch(query)
        saveQuery = SavedQueries(keyword = query.casefold(), data=json.dumps(result))
        db.session.add(saveQuery)
        db.session.commit()
        return result
    


@app.route("/moviedetails/<id>", methods={"GET", "POST"})
@login_required
def moviedetails(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        tmdb_info = {}
        omdb_info = {}
        related_movies = []
        if movie:
            saved_movie = SavedMovies.query.filter_by(id=id).first()
            if not saved_movie:
                tmdb_info, omdb_info = fetchAllDetails(id, movie.imdb_id)
                save_movie = SavedMovies(id=id, imdb_id=movie.imdb_id, keywords=movie.name, tmdb_data=json.dumps(tmdb_info), omdb_data=json.dumps(omdb_info))
                db.session.add(save_movie)
                db.session.commit()
            else:
                tmdb_info = json.loads(saved_movie.tmdb_data)
                omdb_info = json.loads(saved_movie.omdb_data)
            related_movies = fetchSimilarMovies(movie)
            return render_template("details.html", user=current_user, movie=movie, tmdb_info=tmdb_info, omdb_info=omdb_info, related_movies=related_movies, value="hidden")
        else:
            saved_movie = SavedMovies.query.filter_by(id=id).first()
            if not saved_movie:
                tmdb_info = getTMDBRes(id)
                imdb_id = tmdb_info["imdb_id"]
                if imdb_id == None:
                    imdb_id = findIMDBid(tmdb_info["title"])
                omdb_info = getOMDBRes(imdb_id)
                new_movie = SavedMovies(id=id, imdb_id=imdb_id, keywords=tmdb_info["title"], tmdb_data=json.dumps(tmdb_info), omdb_data=json.dumps(omdb_info))
                db.session.add(new_movie)
                db.session.commit()
            else:
                tmdb_info = json.loads(saved_movie.tmdb_data)
                omdb_info = json.loads(saved_movie.omdb_data)
                imdb_id = tmdb_info["imdb_id"]
            moviegenre = omdb_info["Genre"]
            if not moviegenre:
                moviegenre = ""
                for i in tmdb_info["genres"]:
                    moviegenre += i["name"]
                    moviegenre += ", "
            fetchSavedSimilarMovies(moviegenre)
            return render_template("newdetails.html", id=id, user=current_user, imdb_id=imdb_id, tmdb_info=tmdb_info, omdb_info=omdb_info, related_movies=related_movies, itp=imdb_title_prefix, iip=imdb_image_prefix, genre=moviegenre, value="hidden")



@app.route("/request/<string>", methods={"GET", "POST"})
@login_required
def requestmovie(string):
    if request.method == "GET":
        temp = string.split("+")
        id = temp[1]
        rm = MovieRequest.query.filter_by(id=id).first()
        if rm:
            flash(f"You have already requested this Movie!", "warning")
            return redirect("/requestdashboard")
        imdb_url = imdb_title_prefix + temp[0]
        movie = SavedMovies.query.filter_by(id=id).first()
        tmdb_info = json.loads(movie.tmdb_data)
        if tmdb_info["poster_path"]:
            posterLink = imdb_image_prefix + tmdb_info["poster_path"]
        else:
            posterLink = "/static/img/notAvailable.jpg"
        name = tmdb_info["title"]
        original_name = tmdb_info["original_title"]
        release_year = tmdb_info["release_date"].split("-")[0]
        requestor = current_user.email
        requested_movie = MovieRequest(id=id, imdb_URL=imdb_url, posterLink=posterLink, requestor=requestor, release_year=release_year, name=name, original_name=original_name)
        db.session.add(requested_movie)
        db.session.commit()
        flash(f"Movie request submitted!", "success")
        return redirect("/")


@app.route("/requestdashboard", methods={"GET", "POST"})
@login_required
def requestdashboard():
    if request.method == "GET":
        unFulfilled = MovieRequest.query.filter_by(isfulfilled=False).all()
        fulfilled = MovieRequest.query.filter_by(isfulfilled=True).all()
        return render_template("requests.html", user=current_user, unFulfilled=unFulfilled, fulfilled=fulfilled, value="hidden", requestdashboard="active", admincorner="active")


@app.route("/acceptrequest/<id>", methods={"GET", "POST"})
@login_required
def acceptrequest(id):
    if request.method == "GET":
        requestedMovie = MovieRequest.query.filter_by(id=id).first()
        requestedMovie.isfulfilled = True
        requestedMovie.status = "Approved"
        db.session.add(requestedMovie)
        db.session.commit()
        return redirect("/requestdashboard")

@app.route("/denyrequest/<id>", methods={"GET", "POST"})
@login_required
def denyrequest(id):
    if request.method == "GET":
        requestedMovie = MovieRequest.query.filter_by(id=id).first()
        requestedMovie.isfulfilled = True
        requestedMovie.status = "Rejected"
        db.session.add(requestedMovie)
        db.session.commit()
        return redirect("/requestdashboard")


@app.route("/edit/<id>", methods={"GET", "POST"})
@login_required
def edit(id):
    if request.method == "GET":
        movie = Movie.query.filter_by(id=id).first()
        return render_template("edit.html", user=current_user, value="hidden", movie=movie)
    if request.method == "POST":
        id = request.form["id"]
        imdb_id = request.form["imdb_id"]
        name = request.form["name"]
        original_name = request.form["original_name"]
        release_year = request.form["year"]
        posterLink = request.form["posterLink"]
        directLink = request.form["directLink"]
        genre = request.form["genre"]
        language = request.form["language"]
        imdb_rating = request.form["rating"]
        runtime = request.form["runtime"]
        is_adult = request.form["is_adult"]
        is_archived = request.form["is_archived"]
        watch_count = request.form["watch_count"]
        movie = Movie.query.filter_by(id=id).first()
        movie.id = id
        movie.imdb_id = imdb_id
        movie.name = name
        movie.original_name = original_name
        movie.release_year = release_year
        movie.posterLink = posterLink
        movie.directLink = directLink
        movie.genre = genre
        movie.language = language
        movie.imdb_rating = imdb_rating
        movie.runtime = runtime

        if is_adult.casefold() == "False".casefold():
            movie.is_adult = False
        elif is_adult.casefold() == "True".casefold():
            movie.is_adult = True
        
        if is_archived.casefold() == "False".casefold():
            movie.is_archived = False
        elif is_archived.casefold() == "True".casefold():
            movie.is_archived = True
        
        movie.watch_count = watch_count
        db.session.add(movie)
        db.session.commit()
        flash(f"Movie has been updated!", "success")
        redirect_url = "/details/"+id
        return redirect(redirect_url)