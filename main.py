# This is my Cafe and Wify website. It is made using Flask framework for the backend and Bootstrap framework for the front end. 
# I made this website to improve my coding skills and to remember how to autenticate users using Flask and also how to work with databases, such as SQLite and SQLALchemy.
# The database for the cafes can be updated, but users database works perfectly.
# Users can register or log into my website. 

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
# This boolean variable will be used in my index.html file. It removes Log In and Sing Up when user is registered.
user_logged = False

# Configuration for the first database that will hold cafes and users who log in
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['database_name']
# I was going to make forms using Flask-WTF, but then I decided to make them only with Bootstrap, so this is not needed.
app.config['SECRET_KEY'] = os.environ['secret_key']
# Creates my SQLAlchemy database.
db = SQLAlchemy(app)


# Defining my Cafe model here or table from my database that will get hold of the cafes data.
class Cafe(db.Model):
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.String(200))
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.Integer)


# Defining my user model or table from database that will get hold of users data.
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


# This part can be updated in the future, but for now I am leaving it like that.
class SearchForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    submit = SubmitField('Search')


# Here I am defining routes that I will use in my website.
@app.route('/all_cafes', methods=['GET', 'POST'])
def all_cafes():
    form = SearchForm()
    cafes = []

    if form.validate_on_submit():
        location = form.location.data
        cafes = Cafe.query.filter_by(location=location).all()

    return render_template('all_cafes.html', form=form, cafes=cafes)


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('index.html', logged=user_logged)


@app.route('/add-cafe', methods=["GET", "POST"])
def add_cafe():
    if request.method == "POST":
        name = request.form.get("cafeName")
        location = request.form.get("address")
        description = request.form.get("description")

        new_cafe = Cafe(name=name, location=location, rating=description)
        db.session.add(new_cafe)
        db.session.commit()

        return render_template('all_cafes.html')

    return render_template('add_cafe.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_logged
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Checks in the database for a user with the same email as provided one.
        user = User.query.filter_by(email=email).first()

        # If there is user that has this email in my database it will hash the password that this user enter and will check if that password is the same with the one from my database.
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            user_logged = True
            return redirect(url_for('home'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')

    return render_template('login.html')


@app.route('/sing_up', methods=["GET", "POST"])
def sing_up():
    if request.method == "POST":
        # Extracts data from the registration form.
        username = request.form.get("floatingInputName")
        email = request.form.get("floatingInputEmail")
        password = request.form.get("floatingPassword")

        # Hashes the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Creates a new User instance and adds it to the database.
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Redirects the user to the home page.
        global user_logged
        user_logged = True
        return redirect(url_for('home'))

    return render_template('singup.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def log_out():
    global user_logged
    user_logged = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
