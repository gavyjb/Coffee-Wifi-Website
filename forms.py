# -----------------------------This is Portfolio Project 7 of 100 Days of Code on Udemy ---------------------------#
# ----------------------------- Created on 3/16/2022 by Gavra J Buckman --------------------------------------------#
# --------All code is mine.  I certify that I did not copy or plagiarize anyone else's work------------------------#
# Requirement is to create a website to display cafe's that sell coffee and have wi-fi for remote working.
# Using RESTful API, allow users to add new cafes and delete cafes that are no longer open.

# This module holds all the classes that define the different forms used by this website.

# ----------------------------------- IMPORT STATEMENTS ------------------------------------------------------------#
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired
from flask_ckeditor import CKEditorField

# ----------------------------------- CONSTANTS ------------------------------------------------------------#
YES_NO_CHOICES = [(True, 'Yes'), (False, 'No')]


# ----------------------------------- CLASSES --------------------------------------------------------------#
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class ReviewForm(FlaskForm):
    review = CKEditorField("Review", validators=[DataRequired()])
    submit = SubmitField("Submit Review")


class AddCafeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    map_url = StringField("Map URL")
    img_url = StringField("Image URL")
    location = StringField("Location", validators=[DataRequired()])
    has_sockets = SelectField("Has Sockets?", choices=YES_NO_CHOICES, coerce=bool)
    has_toilet = SelectField("Has Toilets?", choices=YES_NO_CHOICES, coerce=bool)
    has_wifi = SelectField("Has Wifi?", choices=YES_NO_CHOICES, coerce=bool)
    can_take_calls = SelectField("Can Make Calls Here?", choices=YES_NO_CHOICES, coerce=bool)
    seats = StringField("Number of Seats", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    city_name = StringField("City Name", validators=[DataRequired()])
    country_abbr = StringField("Country Abbr", validators=[DataRequired()])
    submit = SubmitField("Submit Suggestion")