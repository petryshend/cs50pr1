import os
import requests
import re

from flask import Flask, session, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from user import User
from user_service import UserService


app = Flask(__name__)

API_KEY = 'h57c2PrwpttY6qmJk0I1Cg'

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
    check_login()
    return 'You are logged in as ' + session['user'].email

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = UserService()
    errors = {}
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get_by_email(email)
        if not user or not users.verify_password(user.password, password):
            errors['email'] = 'User or password is not correct'

        if not errors:
            # TODO: session, redirect and go on
            session['user'] = user
            return redirect(url_for('index'))

    return render_template('login.html', errors=errors)

@app.route('/logout', methods=['GET'])
def logout():
    del session['user']
    return redirect(url_for('login'))

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
            user = User(email, password)
            user = users.insert(user)
            # save to session
            session['user'] = user
            # redirect to mail page
            return redirect(url_for('index'))

    return render_template('register.html', errors=errors)

def check_login():
    if not 'user' in session:
        return redirect(url_for('login'))

def validate_form(email, password, password_repeat):
    users = UserService()
    errors = {}
    if (not valid_email(email)):
        errors['email'] = 'Invalid email'
    elif (users.get_by_email(email)):
        errors['email'] = 'User with such email already exists'
    if (len(password) < 4):
        errors['password'] = 'Password should be at least 4 characters long'
    if (password != password_repeat):
        errors['password_repeat'] = 'Passwords does not match'
    return errors

def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.search(regex, email)
