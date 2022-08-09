from curses.ascii import US
#from os import abort
import datetime
import functools
import uuid
from flask import (
    Blueprint, 
    current_app, 
    redirect, 
    render_template, 
    request,
    session,
    url_for,
    flash,
    abort
)
from dataclasses import asdict
from movie_library.forms import ExtendedMovieForm, MovieForms, RegisterForm, LoginForm

from movie_library.models import Movie, User
from passlib.hash import pbkdf2_sha256

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get('email') is None:
            return redirect(url_for(".login"))
        
        return route(*args,**kwargs)
    
    return route_wrapper




@pages.route("/")
@login_required # check if session.email exist
def index():
    user_data = current_app.db.user.find_one({"email":session["email"]})
    user = User(**user_data)
    movie_data = current_app.db.movie.find({'_id':{"$in": user.movies}})
    
    movies = [Movie(**movie) for movie in movie_data]
    
    return render_template(
        "index.html",
        title = "Movies Watchlist",
        movies_data = movies
    )
    

@pages.route("/register", methods = ["GET","POST"])
def register():
    if session.get("email"):
        return redirect(url_form(".index"))
    
    email = ""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id     = uuid.uuid4().hex,
            email   = form.email.data,
            password= pbkdf2_sha256.hash(form.password.data),
        )
        user_exist =  current_app.db.user.find_one({"email":form.email.data})        
        if user_exist:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".register"))

        current_app.db.user.insert_one(asdict(user))
        flash("User registered successfully", "success")
        
        return redirect(url_for(".login"))
    
    return render_template(
        "register.html",
        title="Movies Watchlist - Register",
        form=form,
        email = email
    )


@pages.route("/login", methods = ["GET","POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    email_in = ""
    form = LoginForm()
    if form.validate_on_submit():
        email_in = form.email.data
        user_data =  current_app.db.user.find_one({"email":email_in})
        
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))

        user = User(**user_data) #La informacion recuperda de la DB es arreglada como un objeto User
        
        
        if user and pbkdf2_sha256.verify( form.password.data, user.password):
            # Some Cookies for the session are created, id user and email user are used
            session["user_id"] = user._id
            session["email"] = user.email
            return redirect(url_for(".index"))
        
        flash("Login credentials not correct", category="danger")
        
    
    return render_template(
        "login.html",
        title="Movies Watchlist - Login",
        form=form,
        email = email_in
    )

@pages.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    current_theme = session["theme"]
    session.clear()
    session["theme"] = current_theme
    #del session["user_id"]
    #del session["email"]
    

    return redirect(url_for('.login'))

''' ----------------------- '''

@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_movie():
    form = MovieForms() #creation of the movie form, check how its validate input data

    #if the validation fail
    if form.validate_on_submit():
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data
        )
        #<script>Hola</script>
        
        current_app.db.movie.insert_one( asdict( movie ) ) #current_app is the object where the session is 
        current_app.db.user.update_one(
            {'_id': session['user_id'], },
            {'$push': {'movies':movie._id }}
        ) 
             
             
        return redirect(url_for(".index")) # go to function index()
        
        
    return render_template(
        "new_movie.html",
        title = "Movies Watchlist - Add Movie",
        form = form
    )

@pages.route('/edit/<string:_id>', methods=['GET','POST'])
@login_required
def edit_movie(_id:str ):
    movie_data = current_app.db.movie.find_one({"_id":_id})   
    if not movie_data:
        abort(404)
    movie= Movie(**movie_data)
    
    form = ExtendedMovieForm( obj=movie)
    
    #para post
    if form.validate_on_submit():
        movie.cast          = form.cast.data
        movie.series        = form.series.data
        movie.tags          = form.tags.data
        movie.description   = form.description.data
        movie.video_link    = form.video_link.data

        current_app.db.movie.update_one(
            {"_id":movie._id},
            {"$set":asdict(movie)}
        )
        return redirect(url_for(".movie", _id=movie._id))
    
    #para get
    return render_template("movie_form.html", movie=movie, form=form)


@pages.get('/movie/<string:_id>')
@login_required
def movie(_id:str):
    movie_data = current_app.db.movie.find_one({"_id":_id})
    if not movie_data:
        abort(404)
    movie= Movie(**movie_data)
    return render_template(
        "movie_details.html" ,
        movie=movie
    )
    


#utility

@pages.get('/movie/<string:_id>/rate')
@login_required
def rate_movie(_id): #rating proviene del html al presionar la estrella
    rating = int(request.args.get("rating"))
    current_app.db.movie.update_one({"_id":_id},{"$set":{"rating":rating}})
    return redirect(url_for(".movie", _id=_id))
    
@pages.get('/movie/<string:_id>/watch')
@login_required
def watch_today(_id):
    current_app.db.movie.update_one(
        {"_id":_id},
        {"$set":{"last_watched":datetime.datetime.today()}}
    )
    return redirect(url_for(".movie", _id=_id))


    
@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"]    =   "light"
    else:
        session["theme"]    =   "dark"
    
    #return to source get page, "current_pages is get from html "    
    return redirect( request.args.get("current_page") ) 



@pages.errorhandler(400)  #400
def page_not_found(error):
    return render_template("400.html"), 400


@pages.errorhandler(404)  #400
def page_not_found(error):
    return render_template("404.html"), 404