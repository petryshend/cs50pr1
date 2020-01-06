import re

from flask import Flask, session, render_template, request, redirect, url_for, Response, jsonify
from flask_session import Session

from book_review import BookReview
from book_review_service import BookReviewService
from book_service import BookService
from user import User
from user_service import UserService

app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    if not logged_in():
        return redirect(url_for('login'))
    return redirect(url_for('search'))


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
            session['user'] = user
            return redirect(url_for('index'))

    return render_template('login.html', errors=errors)


@app.route('/logout', methods=['GET'])
def logout():
    if 'user' in session:
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
        if not errors:
            user = User(email, password)
            user = users.insert(user)
            session['user'] = user
            return redirect(url_for('index'))

    return render_template('register.html', errors=errors)


@app.route('/search', methods=['GET'])
def search():
    if not logged_in():
        return redirect(url_for('login'))

    book_service = BookService()
    query = request.args.get('q')
    if query:
        books = book_service.search(query)
    else:
        query = ''
        books = []

    return render_template('search.html', books=books, query=query)


@app.route('/book/<book_id>', methods=['GET'])
def book(book_id):
    if not logged_in():
        return redirect(url_for('login'))

    book_service = BookService()
    book = book_service.get_by_id(book_id)

    book_review_service = BookReviewService()
    review = book_review_service.get_by_book_and_user(book, session['user'])

    return render_template('book.html', book=book, review=review)


@app.route('/book/<book_id>/review', methods=['POST'])
def post_review(book_id):
    if not logged_in():
        return redirect(url_for('login'))

    review = request.form['review']
    rate = request.form['rate']

    book_service = BookService()
    book = book_service.get_by_id(book_id)

    book_review_service = BookReviewService()
    review = BookReview(book, session['user'], review, rate)
    book_review_service.insert(review)

    return redirect(url_for('book', book_id=book_id))


@app.route('/api/<isbn>', methods=['GET'])
def book_info(isbn):
    book_service = BookService()
    book_review_service = BookReviewService()
    books = book_service.search(isbn)
    if not books:
        return Response('Isbn ' + isbn + ' is not found', 404)
    book = books[0]
    reviews = book_review_service.get_reviews(book)
    res = {
        'title': book.title,
        'author': book.author,
        'year': book.year,
        'isbn': book.isbn,
        'review_count': len(reviews),
        'average_score': float(sum(r.rate for r in reviews) / len(reviews))
    }
    return jsonify(res)


def logged_in():
    return 'user' in session


def validate_form(email, password, password_repeat):
    users = UserService()
    errors = {}
    if not valid_email(email):
        errors['email'] = 'Invalid email'
    elif users.get_by_email(email):
        errors['email'] = 'User with such email already exists'
    if len(password) < 4:
        errors['password'] = 'Password should be at least 4 characters long'
    if password != password_repeat:
        errors['password_repeat'] = 'Passwords does not match'
    return errors


def valid_email(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    return re.search(regex, email)
