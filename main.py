# -----------------------------This is Portfolio Project 7 of 100 Days of Code on Udemy ---------------------------#
# ----------------------------- Created on 3/16/2022 by Gavra J Buckman --------------------------------------------#
# --------All code is mine.  I certify that I did not copy or plagiarize anyone else's work------------------------#
# Requirement is to create a website to display cafe's that sell coffee and have wi-fi for remote working.
# Using RESTful API, allow users to add new cafes and delete cafes that are no longer open.

# ----------------------------------- IMPORT STATEMENTS ------------------------------------------------------------#
from flask import Flask, url_for, render_template, redirect, flash, abort, request
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from forms import RegisterForm, LoginForm, ReviewForm, AddCafeForm
from threading import Lock
from functools import wraps
import os
# ------------------------------------CONSTANTS --------------------------------------------------------------------#
DEFAULT_MAP_URL = 'https://www.google.com/maps/@?api=1&map_action=map'
DEFAULT_IMG_URL = 'http://via.placeholder.com/640x360'

# ----------------------------------- APPLICATION SETUP ------------------------------------------------------------#
##INITIALIZE APP AND BOOTSTRAP
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
ckeditor = CKEditor(app)
bootstrap = Bootstrap5(app)

##INITIALIZE GRAVATAR
gravatar = Gravatar(app)

## CONNECT TO DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##INITIALIZE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
Base = declarative_base()


# ----------------------------------- CLASSES ----------------------------------------------------------------------#
# User Table Configuration
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000))

    # Virtual column to allow many to one relationship
    reviews = relationship("Review", backref="author")


# Review Table Configuration
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key relationships
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    cafe_id = db.Column(db.Integer, db.ForeignKey("cafe.id"))

    text = db.Column(db.Text, nullable=False)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)
    city_name = db.Column(db.String(250), nullable=False)
    country_abbr = db.Column(db.String(10), nullable=False)
    is_verified = db.Column(db.Boolean)
    is_closed = db.Column(db.Boolean)

    # Virtual column to allow many to one relationship
    reviews = relationship("Review", backref="cafe")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


# Create all tables
##Lock the thread so that data tables can be created without errors. must import threading
lock = Lock()
with lock:
    db.create_all()


# ------------------------------ APP ROUTES ------------------------------------------------------------------------#
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(execute_route):

    @wraps(execute_route)
    def wrapper(*args, **kwargs):
        #print(current_user.__dict__)
        if current_user.id != 1:
            return abort(403, description="Not Authorized to View This Page")
        #Otherwise continue with the route
        return execute_route(*args, **kwargs)
    return wrapper

def logged_in_only(execute_route):
    @wraps(execute_route)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You must be logged in to perform this action.", "warning")
            return redirect(url_for('login', next_page=execute_route.__name__, **kwargs))
        return execute_route(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        hash_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
        new_user = User(
            email=form.email.data,
            password=hash_password,
            name=form.name.data
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("You've already signed up with that email, log in instead!", 'primary')
            return redirect(url_for("login", next_page='home'))
        else:
            login_user(new_user)
            return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    print(f"The next page to load is {request.args.get('next_page')}")
    print(f"{request.args.get('city_name')}")
    print(f"{request.args.get('cafe_id')}")
    next_page = request.args.get('next_page')
    city_name = request.args.get('city_name')
    cafe_id = request.args.get('cafe_id', type=int)
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("That email does not exist, try again")
        elif check_password_hash(user.password, password):
            login_user(user)
            if cafe_id is None:
                return redirect(url_for(next_page))
            else:
                return redirect(url_for(next_page, city_name=city_name, cafe_id=cafe_id))
        else:
            flash("Password incorrect, please try again.")

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/cities")
def load_cities():
    return render_template("cities.html")


@app.route("/show_all/<city_name>")
def get_all_cafes(city_name):
    #cafes = db.session.query(Cafe).all()
    cafes = Cafe.query.filter_by(city_name=city_name, is_verified=True).all()
    return render_template("cafes.html", all_cafes=cafes, city=city_name)


@app.route("/suggest", methods=["POST", "GET"])
@logged_in_only
def add_place():
    form = AddCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data if form.map_url.data else DEFAULT_MAP_URL,
            img_url=form.img_url.data if form.img_url.data else DEFAULT_IMG_URL,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
            city_name=form.city_name.data,
            country_abbr=form.country_abbr.data,
            is_verified=False,
            is_closed=False
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("suggest.html", form=form)

@app.route("/<city_name>/<int:cafe_id>")
def place_details(cafe_id, city_name):
    cafe = Cafe.query.get(cafe_id)
    return render_template("place.html", cafe=cafe)


## HTTP DELETE - Delete Record
@app.route("/report-closed/<city_name>/<int:cafe_id>", methods=["GET", "POST"])
@logged_in_only
def report_closed(city_name, cafe_id):
    cafe = Cafe.query.get(cafe_id)
    cafe.is_closed = True
    db.session.commit()
    flash(f"Thank you for reporting {cafe.name} as closed.", 'primary')
    return redirect(url_for("place_details", cafe_id=cafe_id, city_name=city_name))


@app.route("/review/<city_name>/<int:cafe_id>", methods=["GET", "POST"])
@logged_in_only
def write_review(city_name, cafe_id):
    cafe = Cafe.query.get(cafe_id)
    form = ReviewForm()
    existing_review = Review.query.filter_by(author_id=current_user.id, cafe_id=cafe_id).first()
    if existing_review:
        return redirect(url_for('edit_review', city_name=city_name, cafe_id=cafe_id, review_id=existing_review.id))

    if form.validate_on_submit():
        new_review = Review(
            text=form.review.data,
            author_id=current_user.id,
            cafe_id=cafe_id,
        )
        db.session.add(new_review)
        db.session.commit()
        return redirect(url_for('place_details', cafe_id=cafe_id, city_name=city_name))

    return render_template("review.html", form=form, cafe=cafe)


@app.route("/review/<city_name>/<int:cafe_id>/<review_id>", methods=["GET", "POST"])
def edit_review(city_name, cafe_id, review_id):
    cafe = Cafe.query.get(cafe_id)
    review = Review.query.get(review_id)
    form = ReviewForm(
        review=review.text
    )
    if form.validate_on_submit():
        review.text = form.review.data
        db.session.commit()
        return redirect(url_for('place_details', cafe_id=cafe_id, city_name=city_name))

    return render_template("review.html", form=form, cafe=cafe)


# ------------------------------ RUN APPLICATION ---------------------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)
