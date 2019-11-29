import os
import requests
import re

from flask import Flask, session, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from user import User
from user_service import UserService

from pprint import pprint

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route('/')
def index():
    apiKey = 'h57c2PrwpttY6qmJk0I1Cg'

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        return 'this is post'
    else:
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    users = UserService()
    errors = []
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        password_repeat = request.form['password_repeat']
        errors = validate_form(email, password, password_repeat)
        if (not errors):
            # save user
            user = new User(email, password)
            user = users.insert(user)
            # save to session

            # redirect to mail page
            return 'SUCCESS'

    return render_template('register.html', errors=errors)

@app.route('/books', methods=['GET'])
def books():
    return 'You should be logged in'

def validate_form(email, password, password_repeat):
    users = UserService()
    errors = {}
    if (not valid_email(email)):
        errors['email'] = 'Invalid email'
    elif (users.user_exists(email)):
        errors['email'] = 'User with such email already exists'
    if (len(password) < 4):
        errors['password'] = 'Password should be at least 4 characters long'
    if (password != password_repeat):
        errors['password_repeat'] = 'Passwords does not match'
    return errors

def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.search(regex, email)
